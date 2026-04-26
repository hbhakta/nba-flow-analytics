from nba_api.stats.endpoints import leaguedashteamstats

class FlowScorer:
    def __init__(self, teams, year):
        self.teams = teams
        self.year = year
        self.raw_data = None
        self.processed_data = None
        
    def fetch_data(self):
        base = leaguedashteamstats.LeagueDashTeamStats(
            season=self.year,
            season_type_all_star="Regular Season",
            per_mode_detailed="PerGame",
            measure_type_detailed_defense="Base",
        ).get_data_frames()[0]
        
        adv = leaguedashteamstats.LeagueDashTeamStats(
            season=self.year,
            season_type_all_star="Regular Season",
            per_mode_detailed="PerGame",
            measure_type_detailed_defense="Advanced",
        ).get_data_frames()[0]

        common_cols = set(base.columns) & set(adv.columns)
        cols_to_keep = list(adv.columns.difference(common_cols)) + ["TEAM_ID"]
        adv = adv[cols_to_keep]
        self.raw_data = base.merge(adv, on="TEAM_ID", how="inner")
        return self
    
    def filter_data(self):
        self.processed_data = self.raw_data[self.raw_data['TEAM_NAME'].isin(self.teams)]
        return self
    
    def __repr__(self):
        status = "filtered" if self.processed_data is not None else "fetched" if self.raw_data is not None else "empty"
        return f"{self.__class__.__name__} | Season: {self.year} | Teams: {self.teams} | Status: {status}"

teams = ['Sacramento Kings', 'Boston Celtics', 'Golden State Warriors']
year = "2022-23"

scorer = FlowScorer(teams, year)
scorer.fetch_data().filter_data()

print(scorer)

