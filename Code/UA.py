import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# class for Uncertainty Analysis
class UA:
    def __init__(self, data):
        self.data = data
        self.alternatives = data.columns.get_level_values(
            0).unique()  # Extract Unique Alternatives

    def get_alternative_matrix(self, alternative):

        if alternative not in self.alternatives:
            raise ValueError(
                f"Alternative '{alternative}' not found in DataFrame.")
        # Extract as a Numpy array
        alternative_matrix = self.data[alternative].values
        return alternative_matrix

    def get_all_matrices(self):

        return {alt: self.get_alternative_matrix(alt) for alt in self.alternatives}

    # Discernability Analysis

    def DA(self, diff):
        """
        The DA : returns the probability
                 that alternative 1 performs 
                 better than alternative 2
        - I've made it so that it gets as 
          input the difference matrix for efficienty
          reasons.
        """
        return np.mean(diff < 0)

    # Ranking Probability : Probability of occurence of rankings

    def RP(self, alt):
        rankings = []
        """
        First it sorts out columns in 
        each row by there values.
        and then stores the result of 
        each row in a tuple and then listed 
        in a list (rankings).
        """
        for _, row in self.data.iterrows():
            sorted_alternatives = row[alt].sort_values().index
            rankings.append(tuple(sorted_alternatives))
        """
        In this part :
        -Converts the array into a Pandas Series.
        -Counts how often each ranking appears.
        -{normalize=True} converts counts into probabilities.
        """
        ranking_counts = pd.Series(rankings).value_counts(normalize=True)
        return ranking_counts
    # Mean&Quantiles : Computation of means and quantiles

    def MQ(self, alt):

        return {
            'mean': self.data[alt].mean(),
            'quantiles': self.data[alt].quantile([0.25, 0.5, 0.75])
        }

    def SMD(self, D):

        return D.mean()/D.std() if D.std() != 0 else 0

    def DRD(self, a1, a2):

        return (a1-a2)/np.max(a1, a2)

    def HSM(self, a1, a2, lambda_value=0.05):

        ratio = a1/a2
        hsm = np.mean(ratio > (1+lambda_value))
        return hsm

    def plot_distribution(self, alternative):

        sns.histplot(self.data[alternative], kde=True)
        plt.title(f'Distribution of {alternative}')
        plt.xlabel('Impact Value')
        plt.ylabel('Frequency')
        plt.show()

    def plot_relative_differences(self, alt1, alt2):

        relative_diff = self.DRD(alt1, alt2)
        sns.boxplot(relative_diff)
        plt.title(f'Relative Differences between {alt1} and {alt2}')
        plt.xlabel('Relative Difference')
        plt.show()
