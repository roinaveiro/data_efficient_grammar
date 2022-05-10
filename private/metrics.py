from rdkit import DataStructs, Chem
from rdkit.Chem import AllChem
import numpy as np
import torch.multiprocessing as mp
from retro_star.api import RSPlanner

from rdkit.Chem import RDConfig
import os
import sys
sys.path.append(os.path.join(RDConfig.RDContribDir, 'SA_Score'))
# now you can import sascore!
import sascorer


class InternalDiversity():
    def distance(self, mol1, mol2, dtype="Tanimoto"):
        assert dtype in ["Tanimoto"]
        if dtype == "Tanimoto":
            sim = DataStructs.FingerprintSimilarity(Chem.RDKFingerprint(mol1), Chem.RDKFingerprint(mol2))
            return 1 - sim
        else:
            raise NotImplementedError

    def get_diversity(self, mol_list, dtype="Tanimoto"):
        similarity = 0
        mol_list = [AllChem.GetMorganFingerprintAsBitVect(x, 3, 2048) for x in mol_list] 
        for i in range(len(mol_list)):
            sims = DataStructs.BulkTanimotoSimilarity(mol_list[i], mol_list[:i])
            similarity += sum(sims)
        n = len(mol_list)
        n_pairs = n * (n - 1) / 2
        diversity = 1 - similarity / n_pairs
        return diversity

class SaScore():
    def get_sascore(self, mol_list):

        sa_scores = [sascorer.calculateScore(x) for x in mol_list]
        
        avg_score = 0.0
        for i in sa_scores:
            avg_score += 1. - (i-1.) / 9.

        return avg_score / len(sa_scores)

class SimilarityTrain():

    def similarity(self, ref_mol, mol_list, dtype="Tanimoto"):

        ref_mol = AllChem.GetMorganFingerprintAsBitVect(ref_mol, 3, 2048) 
        mol_list = [AllChem.GetMorganFingerprintAsBitVect(x, 3, 2048) for x in mol_list] 
        
        sims = DataStructs.BulkTanimotoSimilarity(ref_mol, mol_list)
        
        return np.mean(sims)

    def get_similarity(self, mol_list, dtype="Tanimoto"):

        ref_mol = '[C@@H]1OC(c2ccccc2)O[C@H]2COC(c3ccccc3)O[C@H]21'
        ref_mol = Chem.MolFromSmiles(ref_mol)

        similarity = self.similarity(ref_mol, mol_list)
        return similarity

if __name__ == "__main__":
    pass

