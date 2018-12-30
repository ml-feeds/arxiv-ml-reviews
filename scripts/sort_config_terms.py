from arxivmlrev import config

df = config.CONFIG_TERMS.copy()
df = df.sort_values(['Presence', 'Term'], ascending=[0, 1]).drop_duplicates('Term')
if not df.equals(config.CONFIG_TERMS):
    df.to_csv(config.CONFIG_TERMS_PATH, index=False)
