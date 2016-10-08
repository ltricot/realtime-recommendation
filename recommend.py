"""
    Module's goal is to build a recommendation system for suggesting memes to
users. The model will use data given explicitly by the user (likes and
dislikes) to build recommendations.

    The final recommender class will be built by inheriting from all classes
which bring desired functionality to the system. The classes below are mix-ins
and are therefore not all necessary; when building the final class, make sure
the inheritance order (which determines the method resolution order, or `MRO`)
is right (or use the `Build` metaclass), so that all classes manage to get the
right arguments when their methods are called.

"""


#--internal imports
from testutils import *
from storage import *
from model import *
import skeleton

#--external imports
import pandas as pd
import numpy as np


#--code...
@debug
class DataModel(skeleton.System):
    """
        Inherit from this class and Data mix-ins to have your model
    download its data itself.

    """
    key = 4

    def update(self, data=None, *args, **kwargs):
        """
            Simply fetches data and passes it to the next update method in the
        class's MRO.

        """

        if data is None: data = self.fetch()
        return super().update(data=data.values, *args, **kwargs)

    def suggest(self, users=None):
        """
            Permits the use of user indices (instead of numbers) to recommend.
        Returns a dataframe whose index is a list of users and whose columns is
        a list of object_ids.

        """

        if users is None:
            users = list(range(len(self.data)))
        elif isinstance(users[0], str):
            user_names = list(self.data.index)
            users = [user_names.index(u) for u in users]
        suggestions = pd.DataFrame(
            super().suggest(users),
            index=self.data.index[users],
            columns=self.data.columns)
        # the next lines are weird due to pandas indexing rules
        a, b = self.data.values[users].nonzero()
        suggestions.iloc[tuple(a), tuple(b)] = -1
        return suggestions


@debug
class Build(abc.ABCMeta):
    """
        Specify this metaclass if you don't want to have to deal with mix-in
    inheritance order. Do it. Really.

    """

    def __new__(mcls, name, bases, dictionary):
        return super().__new__(mcls, name,
            tuple(sorted(bases, key=lambda cls: -cls.key)),
            dictionary)
