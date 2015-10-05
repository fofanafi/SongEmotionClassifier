import os.path

class Adder:
  libsvm = '1'
  count = 1

  def __init__(self, data):
    self.data = data

  def add(self, attr):
    v = self.data[attr]
    if attr == 'loudness':
      v = v / 20
    self.libsvm += ' ' + str(self.count) + ':' + str(v)
    self.count += 1
    return self

  def get_string(self):
    return self.libsvm

class WekaAdder(Adder):
  s = ''

  def add(self, attr):
    self.s += str(self.data[attr]) + ','
    return self
  
  def get_string(self):
    return self.s

class Categorizer:
  def __init__(self, labeler, details):
    self.labeler = labeler
    self.details = details

  def categorize(self, song, emotions, verse = '', is_test = False):
    pass

class Labeler:
  emotmap = []
  default = ''

  def label(self, emotions):
    for e in emotions:
      for (emotion, label) in self.emotmap:
        if emotion == e:
          return [label]
    #for (emotion, label) in self.emotmap:
    #  if emotion in emotions:
    #    return label
    return [self.default]

class EverythingLabeler(Labeler):
  def __init__(self):
    self.name = 'alllabels'
    self.labels = 'happy,sad,wistful,regretful,upbeat,angry,crazy,love'

  def label(self, emot):
    if emot.count('strong') > 0:
            emot.remove('strong')
    if emot.count('soft') > 0:
            emot.remove('soft')
    if emot.count('romantic') > 0:
            #emot[ emot.index('romantic') ] = 'love'
            emot.remove('romantic')
    if emot.count('party') > 0:
            emot[ emot.index('party') ] = 'upbeat'
    if not emot:
            emot.append('love')
    return emot

class OriginalLabeler(Labeler):
  def __init__(self):
    self.name = 'original'
    self.labels = 'happy,sad,wistful,regretful,upbeat,angry,crazy,love,romantic,soft,strong,party'
  
  def label(self, emot):
    return emot

class MoodLabeler(Labeler):
  def __init__(self):
    self.name = 'mood'
    happy = 'happy'
    sad = 'sad'
    self.emotmap = [('happy', happy), ('sad', sad), ('wistful', sad),
      ('regretful', sad), ('upbeat', happy), ('party', happy)]
    self.default = 'other'
    self.labels = 'happy,sad,other'

class EnergyLabeler(Labeler):
  def __init__(self):
    self.name = 'energy'
    upbeat = 'upbeat'
    soft = 'soft'
    strong = 'energetic'
    self.emotmap = [('party', strong), ('soft', soft), ('upbeat', strong),
      ('wistful', soft), ('angry', strong), ('crazy', strong),
      ('strong', strong)]
    self.default = 'other'
    self.labels = 'soft,energetic,other'

class LoveLabeler(Labeler):
  def __init__(self):
    self.name = 'love'
    love = 'love'
    self.default = 'other'
    self.emotmap = [('love', love), ('romantic', love)]
    self.labels = 'love,other'

class SVMCategorizer(Categorizer):
  def __init__(self, labeler, details):
    name = labeler.name
    self.out = open('train', 'a')
    self.test = open('testfile', 'a')
    self.train_feats = open('train_feats', 'a')
    self.test_feats = open('test_feats', 'a')
    Categorizer.__init__(self, labeler, details)
    
  def categorize(self, song, emotions, verse, is_test):
    out = self.test if is_test else self.out
    out2 = self.test_feats if is_test else self.train_feats
    emot = self.labeler.label(emotions)
    add_feats = self.get_song_details(song) 
    for e in emot:
      out.write(e + '\t' + verse + '\n')
      out2.write(add_feats + '\n')

  def get_song_details(self, song):
    data = self.details[song]
    return self.get_svm(data)
  
  def get_svm(self, data):
    adder = Adder(data)
    #adder.add('tempo').add('mode').add('energy')
    #adder.add('loudness').add('danceability').add('valence')
    adder.add('energy').add('danceability').add('valence')
    #adder.add('loudness')
    #adder.add('mode')
    return adder.get_string()

class WekaCategorizer(Categorizer):
  def __init__(self, labeler, details):
    filename = labeler.name + '.arff'
    if not os.path.isfile(filename):
      self.out = open(filename, 'a')
      atts = open('attributes').read()
      self.out.write('@RELATION ' + labeler.name + '\n')
      self.out.write(atts)
      self.out.write('@ATTRIBUTE class {' + labeler.labels + '}')
      self.out.write('\n\n@DATA\n')
    else: self.out = open(filename, 'a')
    Categorizer.__init__(self, labeler, details)

  def categorize(self, song, emotions):
    emot = self.labeler.label(emotions)
    add_feats = self.get_song_details(song)
    for e in emot:
      if not e: continue
      self.out.write(add_feats + e + '\n')

  def get_song_details(self, song):
    data = self.details[song]  
    adder = WekaAdder(data)
    adder.add('tempo').add('mode').add('energy')
    adder.add('loudness').add('danceability').add('valence')
    return adder.get_string()


