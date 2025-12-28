from src.demand.domain.events.demand_calculated import on_demand_calculated

class DemandService:
    def __init__(self, repository):
        self._repository = repository

    def calculate_demand(self, df_stations_count, df_residents_geo):
        """
        Coordinates the 'Process Demand' task.
        """
        # 1. Call your logic function (Process)
        results = on_demand_calculated(df_stations_count, df_residents_geo)
        
        # 2. Store it in the repository so the UI can find it
        self._repository.update_analysis(results)
        
        return results

    def get_latest_results(self):
        return self._repository.get_analysis()