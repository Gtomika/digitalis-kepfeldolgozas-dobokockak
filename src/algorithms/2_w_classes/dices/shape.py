import math

class Shape:

    def __init__(self, index, area, length, compactness, circularity, contour, center):
        self._index = index
        self._area = area
        self._length = length
        self._compactness = compactness
        self._circularity = circularity
        self._contour = contour
        self._center = center

    @staticmethod
    def distance(s1, s2):
        return math.sqrt(((s2.center.x - s1.center.x)**2) + ((s2.center.y - s1.center.y)**2))


    @property
    def index(self):
        return self._index


    @property
    def area(self):
        return self._area


    @property
    def length(self):
        return self._length

    
    @property
    def compactness(self):
        return self._compactness

    
    @property
    def circularity(self):
        return self._circularity


    @property
    def contour(self):
        return self._contour


    @property
    def center(self):
        return self._center