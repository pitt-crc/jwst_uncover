import pathlib
import numpy as np

import dash
from dash import html, dcc

from .utils_funcs import (
    navbar_overviews_spec,
    _STYLES,
    _FILTERS_RGB_STR,
    _FILTERS_ALL,
    _IMGTYPES_MORPHOLOGEURS,
)

from .file_io import global_store


dash.register_page(
    __name__,
    path_template="/overviews/spec/<id>",
)


_PAGE_FLAVOR = "Spec Sample"
_VERS = "v1.1"

_VERS_PHOT = "DR3"

path = pathlib.Path(__file__).parent.parent.resolve()
_FNAME_DF = f"{path}/assets/data/df_sample_spec_full.fits"
_DATA_PATH = "/assets/data/cutouts_spec/"


df = global_store(_FNAME_DF)


_DICT_KEYS = {
    "id": "specid",
    "id_phot": "id_DR3",
}


_BREAKS_INFO_ENTRIES = [
    "ra",
    "z_phot_16",
]
_KEYS_INFO = []

_indstart = 0
_keys_orig = np.array(list(df.keys()))
for bkey in _BREAKS_INFO_ENTRIES:
    whkey = np.where(_keys_orig == bkey)[0]
    _indend = whkey[0]
    _KEYS_INFO.append(_keys_orig[_indstart:_indend])
    _indstart = _indend
_KEYS_INFO.append(_keys_orig[_indstart:])


_DICT_TABLE_ENTRIES_FULL = {
    "ra": {
        "format": "0.8f",
    },
    "dec": {
        "format": "0.8f",
    },
    "sep_DR3_epoch1": {
        "format": "0.3f",
    },
    "sep_DR3_epoch2": {
        "format": "0.3f",
    },
}

_DICT_TABLE_ENTRIES_FULL_ADD = {
    "magF444W": {
        "format": "0.3f",
    },
}

_keys_flt_trim_pctl = [
    "z_phot",
    "mu",
    "lmstar",
    "mwa",
    "dust2",
    "lmet",
    "logfagn",
    "z_spec",  # to get _16,_50,_84
]
_keys_flt_trim_pctl_log = [
    "sfr100",
    "ssfr100",
]
_keys_flt_trim = [
    "z_spec",
]

for key in _keys_flt_trim_pctl:
    for pctl in [16, 50, 84]:
        _DICT_TABLE_ENTRIES_FULL_ADD[f"{key}_{pctl}"] = {
            "format": "0.3f",
            "combine_tuple": True,
            "label_extra": " (50 [16,84])",
        }

for key in _keys_flt_trim_pctl_log:
    for pctl in [16, 50, 84]:
        _DICT_TABLE_ENTRIES_FULL_ADD[f"{key}_{pctl}"] = {
            "format": "0.2e",
            "combine_tuple": True,
            "label_extra": " (50 [16,84])",
        }

for key in _keys_flt_trim:
    _DICT_TABLE_ENTRIES_FULL_ADD[f"{key}"] = {
        "format": "0.3f",
    }


_keys_flt_trim = [
    "texp_tot",
]
for key in _keys_flt_trim:
    _DICT_TABLE_ENTRIES_FULL_ADD[f"{key}"] = {
        "format": "0.1f",
    }


_DICT_TABLE_ENTRIES_FULL.update(_DICT_TABLE_ENTRIES_FULL_ADD)


def _make_info_entries(
    ind,
    rowtype="labels",
    keys_list=None,
):
    if rowtype == "labels":
        entries = []
        for key in keys_list:
            combine_tuple = False
            if key in _DICT_TABLE_ENTRIES_FULL.keys():
                combine_tuple = _DICT_TABLE_ENTRIES_FULL[key].get(
                    "combine_tuple", False
                )
            if combine_tuple:
                if key.split("_")[-1] == "50":
                    lbl = "_".join(key.split("_")[:-1])
                    lbl += _DICT_TABLE_ENTRIES_FULL[key].get("label_extra", "")
                    entries.append(
                        html.Td(
                            lbl,
                            style={
                                **_STYLES["info_entries"],
                                "font-weight": "600",
                            },
                        )
                    )
            else:
                entries.append(
                    html.Td(
                        key,
                        style={
                            **_STYLES["info_entries"],
                            "font-weight": "600",
                        },
                    )
                )

    elif rowtype == "entries":
        entries = []

        for key in keys_list:
            fmt = None
            if key in _DICT_TABLE_ENTRIES_FULL.keys():
                fmt = _DICT_TABLE_ENTRIES_FULL[key].get("format", None)

            combine_tuple = False
            if key in _DICT_TABLE_ENTRIES_FULL.keys():
                combine_tuple = _DICT_TABLE_ENTRIES_FULL[key].get(
                    "combine_tuple", False
                )
            if combine_tuple:
                if key.split("_")[-1] == "50":
                    keybase = "_".join(key.split("_")[:-1])

                    if fmt is not None:
                        val50 = f"{df[keybase + '_50'][ind]:{fmt}}"
                        val16 = f"{df[keybase + '_16'][ind]:{fmt}}"
                        val84 = f"{df[keybase + '_84'][ind]:{fmt}}"
                        val = f"{val50} [{val16}, {val84}]"
                    else:
                        val50 = f"{df[keybase + '_50'][ind]}"
                        val16 = f"{df[keybase + '_16'][ind]}"
                        val84 = f"{df[keybase + '_84'][ind]}"
                        val = f"{val50} [{val16}, {val84}]"
                else:
                    val = None

            else:
                if fmt is not None:
                    val = f"{df[key][ind]:{fmt}}"
                else:
                    val = df[key][ind]

            if val is not None:
                if key == "id_DR3":
                    if val == -9999:
                        entries.append(
                            html.Td(
                                val,
                                style={**_STYLES["info_entries"]},
                            )
                        )

                    else:
                        entries.append(
                            html.Td(
                                dcc.Link(
                                    val,
                                    href=f"/overviews/phot/{int(val)}.html",
                                ),
                                style={**_STYLES["info_entries"]},
                            )
                        )
                else:
                    entries.append(
                        html.Td(
                            val,
                            style={**_STYLES["info_entries"]},
                        )
                    )

    else:
        raise ValueError

    return entries


def _make_sed_sfh_pz_entries(objid, objid_phot):
    entries = {}

    # DR3_44407_specid_874_spec.png

    entries["spec"] = [
        html.Td(
            html.Img(
                src=_DATA_PATH + f"spectra/specid_{objid}_spec.png",
                alt=f"Spectrum for {objid}",
                style={**_STYLES["plots_spec_IMG"]},
            ),
            style={**_STYLES["plots_spec"]},
        )
    ]

    entries_sed_sfh_pz = []

    for fluxtype in ["fnu", "flam"]:
        entries_sed_sfh_pz.append(
            html.Td(
                html.Img(
                    src=_DATA_PATH
                    + f"seds/DR3_{objid_phot}_sed_{fluxtype}.png",
                    alt=f"SED/{fluxtype} for {objid}/ {_VERS_PHOT} {objid_phot}",
                    style={**_STYLES["plots_IMG"]},
                ),
                style={**_STYLES["plots"]},
            )
        )
    entries_sed_sfh_pz.append(
        html.Td(
            html.Img(
                src=_DATA_PATH + f"sfhs/DR3_{objid_phot}_SFH.png",
                alt=f"SFH for {objid}/ {_VERS_PHOT} {objid_phot}",
                style={**_STYLES["plots_IMG"]},
            ),
            style={**_STYLES["plots"]},
        )
    )
    entries_sed_sfh_pz.append(
        html.Td(
            html.Img(
                src=_DATA_PATH + f"Pzs/specid_{objid}_Pz.png",
                alt=f"P(z) for {objid}/ {_VERS_PHOT} {objid_phot}",
                style={**_STYLES["plots_IMG"]},
            ),
            style={**_STYLES["plots"]},
        )
    )

    entries["sed_sfh_pz"] = entries_sed_sfh_pz

    return entries


def _make_rgb_segmap_entries(objid):
    entries = [
        html.Td(
            html.Img(
                src=_DATA_PATH
                + f"RGB_stamps/PSF_BCG-MATCH/{objid}_{filt}.png",
                alt=f"RGB {filt} postage stamp for {objid}",
                style={**_STYLES["rgb_seg_stamps_IMG"]},
            ),
            style={**_STYLES["rgb_seg_stamps"]},
        )
        for filt in _FILTERS_RGB_STR
    ]

    entries.append(
        html.Td(
            html.Img(
                src=_DATA_PATH + f"RGB_stamps/PSF_BCG-MATCH/{objid}_MB.png",
                alt=f"RGB MB postage stamp for {objid}",
                style={**_STYLES["rgb_seg_stamps_IMG"]},
            ),
            style={**_STYLES["rgb_seg_stamps"]},
        )
    )

    entries.append(
        html.Td(
            html.Img(
                src=_DATA_PATH + f"segmap_stamps/{objid}_segLW.png",
                alt=f"Segmap postage stamp for {objid}",
                style={**_STYLES["rgb_seg_stamps_IMG"]},
            ),
            style={**_STYLES["rgb_seg_stamps"]},
        )
    )

    entries.append(
        html.Td(
            html.Img(
                src=_DATA_PATH + f"magmap_stamps/{objid}_magclosest.png",
                alt=f"Magnification postage stamp for {objid}",
                style={**_STYLES["rgb_seg_stamps_IMG"]},
            ),
            style={**_STYLES["rgb_seg_stamps"]},
        )
    )

    entries.append(
        html.Td(
            html.Img(
                src=_DATA_PATH
                + f"msa_shutter_stamps/{objid}_F444W_slitlets.png",
                alt=f"Shutter postage stamp for {objid}",
                style={**_STYLES["rgb_seg_stamps_IMG"]},
            ),
            style={**_STYLES["rgb_seg_stamps"]},
        )
    )

    return entries


def _make_morph_stamp_entries(objid_phot, imgtype="img"):
    if imgtype in _IMGTYPES_MORPHOLOGEURS[1:]:
        if imgtype == "mask":
            entries = [
                html.Td(
                    html.Img(
                        src=_DATA_PATH
                        + f"morph_stamps/ID_DR3_{objid_phot}_F444W_{imgtype}.png",
                        alt="",
                        style={**_STYLES["pstamps_gallery_IMG"]},
                    ),
                    style={**_STYLES["pstamps_gallery"]},
                )
                for filt in _FILTERS_ALL
            ]
        else:
            entries = [
                html.Td(
                    html.Img(
                        src=_DATA_PATH
                        + f"morph_stamps/ID_DR3_{objid_phot}_{filt}_{imgtype}.png",
                        alt="",
                        style={**_STYLES["pstamps_gallery_IMG"]},
                    ),
                    style={**_STYLES["pstamps_gallery"]},
                )
                for filt in _FILTERS_ALL
            ]

        entries_out = [
            html.Td(
                imgtype.capitalize(),
                style={**_STYLES["pstamps_gallery_rowlabel"]},
            ),
        ]

        entries_out.extend(entries)
    else:
        # Labels row entries:

        entries = [
            html.Td(
                filt,
                style={**_STYLES["pstamps_gallery_collabel"]},
            )
            for filt in _FILTERS_ALL
        ]

        entries_out = [
            html.Td("", style={**_STYLES["pstamps_gallery_rowlabel"]})
        ]
        entries_out.extend(entries)

    return entries_out


def layout(id="1.html", page_flavor=_PAGE_FLAVOR, vers=_VERS, **kwargs):
    objid = np.int64(id.split(".html")[0])

    ind = np.where(df[_DICT_KEYS["id"]] == objid)[0][0]

    objid_phot = df[_DICT_KEYS["id_phot"]][ind]

    entries_sed_sfh_pz = _make_sed_sfh_pz_entries(objid, objid_phot)

    entries_rgb_segmap = _make_rgb_segmap_entries(objid)

    entries_morph = {}
    for imgtype in _IMGTYPES_MORPHOLOGEURS:
        entries_morph[imgtype] = _make_morph_stamp_entries(
            objid_phot, imgtype=imgtype
        )

    entries_galprops = {}

    for jj, keys_list in enumerate(_KEYS_INFO):
        for enttype in ["labels", "entries"]:
            entries_galprops[f"{enttype}_{jj}"] = _make_info_entries(
                # objid, objid_phot,
                ind,
                rowtype=enttype,
                keys_list=keys_list,
            )

    overviewlayout = html.Div(
        [
            html.Div(
                [
                    html.H2(
                        children=[
                            html.A(
                                "UNCOVER",
                                href="https://jwst-uncover.github.io",
                            ),
                            f" Data Viewer: {page_flavor} {vers}",
                        ],
                        style={"margin-bottom": "0"},
                    ),
                ],
            ),
            ### Links / pseudo navbar
            navbar_overviews_spec(),
            ### Galaxy properties
            html.Div(
                className="row",
                style={**_STYLES["plot_divs"], "margin-top": "0.5rem"},
                children=[
                    html.Div(
                        className="column",
                        children=[
                            html.H5(f"Overview: {objid}"),
                            html.Table(
                                className="nopad",
                                children=[
                                    html.Tr(
                                        entries_galprops[enttype],
                                        style={**_STYLES["row_info"]},
                                    )
                                    for enttype in entries_galprops.keys()  # ["labels", "entries"]
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            ### RGB stamps + segmap
            html.Div(
                className="row",
                style={**_STYLES["plot_divs"]},
                children=[
                    html.Div(
                        className="column",
                        children=[
                            html.H6("RGB images"),
                            html.Table(
                                className="nopad",
                                children=[
                                    html.Tr(
                                        entries_rgb_segmap,
                                        style={**_STYLES["row_images"]},
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            ### Spectrum + SED + SFH + p(z)
            html.Div(
                className="row",
                style={**_STYLES["plot_divs"]},
                children=[
                    html.Div(
                        className="column",
                        children=[
                            html.H6("Spectrum + SED + SFH + p(z)"),
                            html.Table(
                                className="nopad",
                                children=[
                                    html.Tr(
                                        entries_sed_sfh_pz[plottype],
                                        style={**_STYLES["row_images"]},
                                    )
                                    for plottype in entries_sed_sfh_pz.keys()
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            ### Morphologeurs
            html.Div(
                className="row",
                style={**_STYLES["plot_divs"]},
                children=[
                    html.Div(
                        className="column",
                        children=[
                            html.H6("Morphologeurs"),
                            html.Table(
                                className="nopad",
                                children=[
                                    html.Tr(
                                        entries_morph[imgtype],
                                        style={**_STYLES["row_images"]},
                                    )
                                    for imgtype in entries_morph.keys()
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            ###
        ]
    )

    return overviewlayout
