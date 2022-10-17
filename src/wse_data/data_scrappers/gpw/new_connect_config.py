from typing import Union

from pydantic import BaseModel


class NewConnectConfig(BaseModel):
    # https://newconnect.pl/notowania
    companies_requests: list[tuple[str, dict[str, str]]] = [
        (
            "https://newconnect.pl/ajaxindex.php",
            {
                "action": "NCExternalDataFrontController",
                "start": "showTable",
                "type": "All",
                "system_type": "",
                "tab": "search",
                "lang": "PL",
                "full": "1",
                "format": "html",
                "filters[segments]": "NC Base,NC Alert,NC Focus,",
                "filters[search]": "",
                "filters[letter]": "",
                "showColumn": "on,on,off,on,off,on,on,on,on,on,on,on,on,off,on,on,on,on,on,off,",
            },
        )
    ]
    # https://newconnect.pl/spolki-komunikaty-spolek
    reports_url: str = "https://newconnect.pl/ajaxindex.php"
    reports_query_params: dict[str, Union[str, list[str]]] = {
        "action": "GPWEspiReportUnion",
        "start": "ajaxSearch",
        "page": "spolki-komunikaty-spolek",
        "format": "html",
        "lang": "PL",
        "categoryRaports[]": ["EBI", "ESPI"],
        "typeRaports[]": ["RB", "P", "Q", "O", "R"],
    }
