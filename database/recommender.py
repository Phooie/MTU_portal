import pandas as pd
from scipy.sparse import coo_matrix
from implicit.als import AlternatingLeastSquares

class ResourceRecommender:
    def __init__(self):
        self.model = AlternatingLeastSquares(
            factors=64,
            iterations=20,
            regularization=0.1
        )
        self.student_map = {}
        self.resource_map = {}
        self.inverse_student_map = {}
        self.inverse_resource_map = {}

    def prepare_matrix(self, interactions):
        students = interactions['student_id'].unique()
        resources = interactions['resource_id'].unique()

        self.student_map = {sid: idx for idx, sid in enumerate(students)}
        self.resource_map = {rid: idx for idx, rid in enumerate(resources)}
        self.inverse_student_map = {idx: sid for sid, idx in self.student_map.items()}
        self.inverse_resource_map = {idx: rid for rid, idx in self.resource_map.items()}

        rows = interactions['student_id'].map(self.student_map)
        cols = interactions['resource_id'].map(self.resource_map)
        data = interactions['weight']

        matrix = coo_matrix((data, (rows, cols)))
        return matrix

    def train(self, interactions):
        matrix = self.prepare_matrix(interactions)
        self.model.fit(matrix)

    def recommend(self, student_id, N=5):
        if student_id not in self.student_map:
            return []
        user_index = self.student_map[student_id]
        recommended = self.model.recommend(user_index, None, N=N)
        return [self.inverse_resource_map[i] for i, _ in recommended]