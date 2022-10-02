from typing import Union

from pydantic import BaseModel


class GPWConfig(BaseModel):
    companies_requests: list[tuple[str, dict[str, str]]] = [
        (
            "https://www.gpw.pl/ajaxindex.php",
            {
                "action": "GPWQuotations",
                "start": "showTable",
                "type": "",
                "tab": "search",
                "lang": "PL",
                "full": "1",
                "format": "html",
                "filters[sectors]": "510,110,750,410,310,360,740,180,220,650,350,320,610,690,660,330,820,399,150,640,540,140,830,790,520,210,170,730,420,185,370,630,130,620,720,710,810,430,120,450,160,530,440,none,",  # noqa
                "filters[indexs]": "WIG20,mWIG40,sWIG80,WIG30,WIG,WIGdiv,WIG_CEE,WIG_Poland,CEEplus,INNOVATOR,mWIG40TR,NCIndex,sWIG80TR,WIG_banki,WIG_budownictwo,WIG_chemia,WIG_energia,WIG_ESG,WIG_górnictwo,WIG_gry,WIG_informatyka,WIG_leki,WIG_media,WIG_motoryzacja,WIG_nieruchomości,WIG_odzież,WIG_paliwa,WIG_spożywczy,WIG_Ukraine,WIG.GAMES5,WIG.MS_BAS,WIG.MS_FIN,WIG.MS_PET,WIG140,WIGtech,WIGtechTR,none,",  # noqa
                "filters[search]": "",
                "filters[letter]": "",
                "showColumn": "on,on,on,off,on,on,on,on,on,on,on,on,on,off,on,off,off,off,off,on,on,off,",
            },
        ),
        (
            "https://www.gpw.pl/ajaxindex.php",
            {
                "action": "GPWQuotations",
                "start": "listSingle",
                "type": "fix1",
                "tab": "search",
                "lang": "PL",
                "full": "1",
                "format": "html",
                "filters[sectors]": "",
                "filters[indexs]": "",
                "filters[search]": "",
                "filters[letter]": "",
                "showColumn": "on,on,on,off,on,on,on,on,on,on,on,on,on,off,on,off,off,off,off,on,on,off,",
            },
        ),
        (
            "https://www.gpw.pl/ajaxindex.php",
            {
                "action": "GPWQuotations",
                "start": "listSingle",
                "type": "fix2",
                "tab": "search",
                "lang": "PL",
                "full": "1",
                "format": "html",
                "filters[sectors]": "",
                "filters[indexs]": "",
                "filters[search]": "",
                "filters[letter]": "",
                "showColumn": "on,on,on,off,on,on,on,on,on,on,on,on,on,off,on,off,off,off,off,on,on,off,",
            },
        ),
    ]
    reports_url: str = "https://www.gpw.pl/ajaxindex.php"
    reports_query_params: dict[str, Union[str, list[str]]] = {
        "action": "GPWEspiReportUnion",
        "start": "ajaxSearch",
        "page": "komunikaty",
        "format": "html",
        "lang": "PL",
        "categoryRaports[]": ["EBI", "ESPI"],
        "typeRaports[]": ["RB", "P", "Q", "O", "R"],
    }
