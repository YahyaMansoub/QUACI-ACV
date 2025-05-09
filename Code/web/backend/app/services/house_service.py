"""
Service pour la gestion des maisons et leurs données associées.
Ce fichier contient la logique métier liée aux maisons, séparée des routes.
"""

from app.models.house import House
from app.models.material import Material
from app.utils.calculation import calculate_impact

class HouseService:
    @staticmethod
    def get_all_houses():
        """
        Récupère toutes les maisons.
        
        Returns:
            list: Liste de tous les objets House
        """
        return House.query.all()
    
    @staticmethod
    def get_house_by_id(house_id):
        """
        Récupère une maison par son ID.
        
        Args:
            house_id (int): ID de la maison
            
        Returns:
            House: Objet House ou None si non trouvé
        """
        return House.query.get(house_id)
    
    @staticmethod
    def create_house(data):
        """
        Crée une nouvelle maison.
        
        Args:
            data (dict): Données de la maison
            
        Returns:
            House: Objet House créé
        """
        house = House(**data)
        house.save()
        return house
    
    @staticmethod
    def update_house(house_id, data):
        """
        Met à jour une maison existante.
        
        Args:
            house_id (int): ID de la maison
            data (dict): Données à mettre à jour
            
        Returns:
            House: Objet House mis à jour ou None si non trouvé
        """
        house = HouseService.get_house_by_id(house_id)
        if house:
            for key, value in data.items():
                setattr(house, key, value)
            house.save()
        return house
    
    @staticmethod
    def delete_house(house_id):
        """
        Supprime une maison.
        
        Args:
            house_id (int): ID de la maison
            
        Returns:
            bool: True si supprimé, False sinon
        """
        house = HouseService.get_house_by_id(house_id)
        if house:
            house.delete()
            return True
        return False
    
    @staticmethod
    def calculate_house_impacts(house_id):
        """
        Calcule l'impact environnemental d'une maison.
        
        Args:
            house_id (int): ID de la maison
            
        Returns:
            dict: Impacts calculés par catégorie
        """
        house = HouseService.get_house_by_id(house_id)
        if not house:
            return None
            
        # Exemple de calcul d'impact (à adapter selon votre logique métier)
        materials = house.materials
        return calculate_impact(materials, house.lifespan)