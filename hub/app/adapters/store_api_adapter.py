import logging
import requests
from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_data: ProcessedAgentData):
        url = f"{self.api_base_url}/agent_data"

        payload = processed_data.model_dump()
        
        try:
            res = requests.post(url, json=payload)
            
            if res.status_code == 201:
                logging.info("Дані успішно відправлені в API.")
                return True

            logging.info(f"Запит не пройшов. Статус код: {res.status_code}")
            return False
            
        except Exception as e:
            logging.info(f"Виникла помилка при з'єднанні з сервером: {e}")
            return False

