import json
import pandas as pd
import re

DADOS_GOV_SOURCES = {
    "dados_gov_municipios": "https://dados.gov.pt/pt/datasets/r/a86ec6e5-f124-4046-9514-903741d2ec25",
    "dados_gov_freg":  "https://dados.gov.pt/pt/datasets/r/82f9ba36-c952-43aa-a103-43d8e093bdac",
    "dados_gov_admin_pub": "https://dados.gov.pt/pt/datasets/r/734537a6-4d8d-4d45-98b0-70902c3946fb",
    "dados_gov_açores": "https://dados.gov.pt/pt/datasets/r/ad34648e-3e89-4e42-a22c-0cbdcd6372ca",
    "dados_gov_madeira": "https://dados.gov.pt/pt/datasets/r/24c02276-486f-47cf-9d9b-6b7cd2e59fb8",
    "dados_gov_presença": "https://dados.gov.pt/pt/datasets/r/c2afba19-9872-4e3a-a616-64f4a61acca9",
    "dados_gov_univ_pub": "https://dados.gov.pt/pt/datasets/r/3dc57d0c-1ccd-48fe-954a-1c4d2fdb6705"
}

OUTPUT_PATH = "resources/governmental_websites/interm/dadosgov.json"

def read_dados_gov_files() -> pd.DataFrame:
    """ read dados gov xlsx file"""
    dfs = []
    for dados_gov_source, dados_gov_url in DADOS_GOV_SOURCES.items():
        # read the excel files
        if "univ" in dados_gov_source:
            uni_dfs = []
            for sheet_name in ["Ensino Univ. Público", "Ensino Pol. Público"]:
                df = pd.read_excel(dados_gov_url, sheet_name=sheet_name).iloc[2:, 0:2]
                df.columns = ["page_name", "url"]
                df["entity"] = df["page_name"]
                uni_dfs.append(df)
            df = pd.concat(uni_dfs)
        else:
            df = pd.read_excel(dados_gov_url, sheet_name=0)
            # filter relevant columns and rename
            if "presença" in dados_gov_source:
                df.columns = ["page_name", "url", "entity"]
            else:
                if "municipios" in dados_gov_source:
                    df = df.iloc[2:, 1:3]
                elif "freg" in dados_gov_source:
                    df = df.iloc[1:,[3, 4]]
                elif "madeira" in dados_gov_source:
                    df = df.iloc[2:, [0, 2]]
                elif "açores" in dados_gov_source:    
                    df = df.iloc[2:,0:2]
                else:
                    df = df.iloc[:,0:2]
                df.columns = ["page_name", "url"]
                df["entity"] = df["page_name"]
        # filter out none values
        df.dropna(inplace=True)
        dfs.append(df)
    return pd.concat(dfs)

def main() -> None:
    """ read the xlsx files and covert to json """
    # clean up and merge
    dados_gov_df = read_dados_gov_files().drop_duplicates(subset=["url"])
    # remove empty cols
    dados_gov_df.dropna(how='all', axis=1, inplace=True)
    dados_gov_df.reset_index(drop = True, inplace=True)
    dados_gov_dict = dados_gov_df.to_dict(orient="index")
    with open(OUTPUT_PATH, "w") as f:
        json.dump(dados_gov_dict, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
    
    