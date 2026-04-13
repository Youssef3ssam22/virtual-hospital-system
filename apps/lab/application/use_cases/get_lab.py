"""Read use cases for lab data retrieval."""

from shared.domain.exceptions import EntityNotFound

from apps.lab.domain.repositories import LabOrderRepository


class GetLabUseCase:
    def __init__(self, repository: LabOrderRepository):
        self.repository = repository

    def order_by_id(self, order_id: str):
        order = self.repository.get_by_id(order_id)
        if not order:
            raise EntityNotFound("LabOrder", order_id)
        return order

    def orders_for_patient(self, patient_id: str):
        return self.repository.list_for_patient(patient_id)

    def pending_orders(self):
        return self.repository.list_pending()

    def results_for_order(self, order_id: str):
        return self.repository.list_results(order_id)
