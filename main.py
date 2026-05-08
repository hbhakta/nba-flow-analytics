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

        # print(self.raw_data.columns)
        return self
    
    def filter_data(self):
        self.processed_data = self.raw_data[self.raw_data['TEAM_NAME'].isin(self.teams)]
        return self
    
    def __repr__(self):
        status = "filtered" if self.processed_data is not None else "fetched" if self.raw_data is not None else "empty"
        return f"{self.__class__.__name__} | Season: {self.year} | Teams: {self.teams} | Status: {status}"

    def compute_ofs(self):
        # print(self.raw_data.describe())
        stats_of_interest = ['PACE', 'AST_PCT', 'AST_TO', 'EFG_PCT']
        
        population_data_mean = self.raw_data[stats_of_interest].mean()
        population_data_std = self.raw_data[stats_of_interest].std()
        
        for stat in stats_of_interest:
            self.raw_data[f'z_{stat}'] = (self.raw_data[stat] - population_data_mean[stat]) /population_data_std[stat]
        
        stats_of_interest_z = [f"z_{x}" for x in stats_of_interest]
        print(self.raw_data[stats_of_interest_z].head())
        self.raw_data['ofs'] = self.raw_data[stats_of_interest_z].sum(axis = 1)
        print(self.raw_data['ofs'].head())

        return self


def main():
    teams = ['Sacramento Kings', 'Boston Celtics', 'Golden State Warriors']
    year = "2022-23"

    scorer = FlowScorer(teams, year)
    # scorer.fetch_data().filter_data().compute_ofs()
    scorer.fetch_data().compute_ofs().filter_data() #compute ofs for all teams to calculate population stats 

    print(scorer)

if __name__ == "__main__":
    main()