"""
    Goal of this module: Define the behavior of classes implemented for the
realtime recommender system through python abstract classes.

"""


#--internal imports
from testutils import debug

#--built-in imports
import abc


#--code...
@debug
class Model(abc.ABC):
    """
        Abstract class defining the behavior of recommendation models. All
    suggest systems are forced to follow the rules set by this class. These
    methods' behaviors are therefore something you can rely on.

    """

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        """
            Updates model's knowledge with given data and learning parameters.
        Learning paramteters depend on the model (MF or neighborhood) that you
        use but also on the mix-ins that you wrap over your model.

        return-type: none

        """

        raise NotImplementedError

    @abc.abstractmethod
    def suggest(self, user=None):
        """
            Practical use of the model, return recommendation for all users
        except if user (index) is given. In this case it returns only the given
        user's recommendation.

        return-type: np.ndarray

        """

        raise NotImplementedError

    @abc.abstractmethod
    def test(self, data, truth):
        """
            Tests the model's accuracy. The smaller the result, the better the
        model performs. (This is evaluated differently depending on the model
        used, do not rely on this to compare MF and Neighborhood).

        return-type: float

        """

        raise NotImplementedError


@debug
class Data(abc.ABC):
    """
        Defines interface which needs to be accessible from the class created
    with the mix-ins underneath.

    """

    @abc.abstractmethod
    def fetch():
        """
            Downloads data and invokes the parse method defined underneath
        before returning this data.

        return-type: pandas.DataFrame

        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse():
        """
            Takes data of a given format (determined by the subclass) and
        returns a pandas.DataFrame representing the user-item matrix used for
        training recommender systems.

        return-type: pandas.DataFrame

        """
        raise NotImplementedError

    @abc.abstractmethod
    def export():
        """
            Exports suggest data to a defined location (such as google cloud
        storage).

        """
        raise NotImplementedError


@debug
class System(Data, Model):
    """
        Meeting point between the data management classes and the recommender
    model classes. Abstract class.

    """
    ...
