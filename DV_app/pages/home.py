import dash

from dash import html

from .utils_funcs import navbar_home


_PAGE_FLAVOR = "Home"
_VERS = "phot/DR3, spec/v1.1"


def setup_all(
    page_flavor=_PAGE_FLAVOR,
    vers=_VERS,
):
    dash.register_page(
        __name__,
        path="/",
        title=f"UNCOVER Data Viewer: {page_flavor} {vers}",
    )

    layout = html.Div(
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
            navbar_home(),
        ]
    )

    return layout


layout = setup_all()
