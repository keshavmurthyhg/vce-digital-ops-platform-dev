from modules.search.filters import apply_filters
from modules.search.search import apply_search


def apply_all_filters(df, status, priority, keyword):

    if status:
        df = df[df["Status"].isin(status)]

    if priority:
        df = df[df["Priority"].isin(priority)]

    df = apply_search(df, keyword)

    return df
