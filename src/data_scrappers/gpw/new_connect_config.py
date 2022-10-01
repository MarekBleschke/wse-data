from typing import Union

from pydantic import BaseModel


class NewConnectConfig(BaseModel):
    companies_url: str = "https://newconnect.pl/ajaxindex.php"
    # fmt: off
    companies_query_params: dict[str, str] = {"format": "html", "lang": "PL", "letter": "", "action": "NCCompany", "start": "listAjax", "order": "ncc_name", "order_type": "ASC", "searchText": "", "countries[1000]": "on", "countries[1002]": "on", "countries[1003]": "on", "countries[1004]": "on", "countries[1005]": "on", "countries[1006]": "on", "countries[1007]": "on", "marketSectors[621]": "on", "marketSectors[441]": "on", "marketSectors[519]": "on", "marketSectors[611]": "on", "marketSectors[750]": "on", "marketSectors[632]": "on", "marketSectors[419]": "on", "marketSectors[411]": "on", "marketSectors[412]": "on", "marketSectors[312]": "on", "marketSectors[443]": "on", "marketSectors[541]": "on", "marketSectors[590]": "on", "marketSectors[361]": "on", "marketSectors[230]": "on", "marketSectors[212]": "on", "marketSectors[180]": "on", "marketSectors[622]": "on", "marketSectors[222]": "on", "marketSectors[190]": "on", "marketSectors[131]": "on", "marketSectors[322]": "on", "marketSectors[650]": "on", "marketSectors[359]": "on", "marketSectors[690]": "on", "marketSectors[660]": "on", "marketSectors[631]": "on", "marketSectors[829]": "on", "marketSectors[415]": "on", "marketSectors[413]": "on", "marketSectors[633]": "on", "marketSectors[612]": "on", "marketSectors[522]": "on", "marketSectors[150]": "on", "marketSectors[432]": "on", "marketSectors[414]": "on", "marketSectors[531]": "on", "marketSectors[649]": "on", "marketSectors[549]": "on", "marketSectors[512]": "on", "marketSectors[149]": "on", "marketSectors[0]": "on", "marketSectors[830]": "on", "marketSectors[790]": "on", "marketSectors[521]": "on", "marketSectors[821]": "on", "marketSectors[290]": "on", "marketSectors[644]": "on", "marketSectors[170]": "on", "marketSectors[730]": "on", "marketSectors[513]": "on", "marketSectors[641]": "on", "marketSectors[370]": "on", "marketSectors[643]": "on", "marketSectors[639]": "on", "marketSectors[629]": "on", "marketSectors[634]": "on", "marketSectors[141]": "on", "marketSectors[532]": "on", "marketSectors[720]": "on", "marketSectors[823]": "on", "marketSectors[822]": "on", "marketSectors[710]": "on", "marketSectors[810]": "on", "marketSectors[431]": "on", "marketSectors[439]": "on", "marketSectors[351]": "on", "marketSectors[129]": "on", "marketSectors[421]": "on", "marketSectors[422]": "on", "marketSectors[450]": "on", "marketSectors[160]": "on", "marketSectors[642]": "on", "marketSectors[142]": "on", "marketSectors[539]": "on", "marketSectors[442]": "on", "marketSectors[423]": "on", "marketSectors[449]": "on", "marketSectors[132]": "on", "marketSectors[511]": "on", "provinces[2]": "on", "provinces[3]": "on", "provinces[4]": "on", "provinces[5]": "on", "provinces[6]": "on", "provinces[7]": "on", "provinces[8]": "on", "provinces[9]": "on", "provinces[10]": "on", "provinces[11]": "on", "provinces[12]": "on", "provinces[13]": "on", "provinces[14]": "on", "provinces[15]": "on", "provinces[16]": "on", "provinces[17]": "on",}  # noqa
    # fmt: on
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
