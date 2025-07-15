import pandas as pd
from typing import List

def load_and_merge(paths: List[str]) -> pd.DataFrame:
    dfs = []
    for p in paths:
        df = pd.read_csv(p)
        # ensure both are floats (or both ints)
        df['X1'] = df['X1'].astype(float)
        df['X2'] = df['X2'].astype(float)
        dfs.append(df)
    # inner‐join all on X1,X2
    df = dfs[0]
    for d in dfs[1:]:
        df = df.merge(d, on=['X1','X2'], how='inner')
    return df
