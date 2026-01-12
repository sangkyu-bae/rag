from typing import Dict, List, Any, Optional
import pandas as pd

class PandasParser():
    def execute(self):
        pass

    def read(
            self,
            path: str,
            dtype: Optional[type] = str,
            header: int = 0,
            skiprows: Optional[int] = None,
            nrows: Optional[int] = None,
    ) -> None:

        self._dfs = pd.read_excel(
            path,
            sheet_name=None,
            engine="openpyxl",
            dtype=dtype,
            header=header,
            skiprows=skiprows,
            nrows=nrows,
        )