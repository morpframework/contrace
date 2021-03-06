import random
import time
import os
import json
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from matplotlib.animation import writers

WORLD = {
    'width': 100,
    'height': 100
}

POPULATION = 2000
CELLSIZE = 10
INFECT_RADIUS = 1
INFECT_PROBABILITY = 0.05
DAY_SIZE = 5

TOWER_LOG = []
INFECT_LOG = []


def tower_log(payload):
    TOWER_LOG.append(payload)


def infect_log(payload):
    INFECT_LOG.append(payload)

def basealpha(num):
    num = int(num)
    res = ''
    up = int(num / 26)
    bal = num % 26
    if up:
        res += basealpha(up - 1)
    res += chr(bal + 65)
    return res


class Area(object):

    def __init__(self, x1, y1, x2, y2):
        assert x1 < x2
        assert y1 < y2

        self.topleft = {'x': x1, 'y': y1}
        self.bottomright = {'x': x2, 'y': y2}

    def contains(self, x, y):
        if ((self.topleft['x'] <= x and self.topleft['y'] <= y)
                and self.bottomright['x'] >= x and self.bottomright['y'] >= y):
            return True
        return False

    def find_people(self, world):
        for person in world.people:
            if self.contains(person.x, person.y):
                yield person

class CellTower(Area):
    
    def __init__(self, cellid, world, *args, **kwargs):
        self.id = cellid
        self.world = world
        super().__init__(*args, **kwargs)
        self.people = []

    def handle_notification(self, person):
        incell = self.contains(person.x, person.y)
        if incell and person in self.people:
            return

        if incell and person not in self.people:
            self.people.append(person)
            tower_log({'timestamp': self.world.time, 'cell_id': self.id, 'event':
                'Enter Cell', 'person_id': person.id})

        if not incell and person in self.people:
            self.people.remove(person)
            tower_log({'timestamp': self.world.time, 'cell_id': self.id, 'event':
                'Leave Cell', 'person_id': person.id})





class World(object):

    def __init__(self, width=WORLD['width'], height=WORLD['height']):
        self.width = width
        self.height = height
        self.index = {}
        for x in range(width):
            for y in range(height):
                self.index[(x,y)] = []

        self.y_index = {}
        self.people = []
        self.towers = []
        self.time = 0
        self.infected_count = 1
        self.infect_history = []
        self.infect_rate_history = []
        cidx = 0
        for x in range(0, width, CELLSIZE):
            cidy = 0
            for y in range(0, height, CELLSIZE):
                cell_id = '{}-{}'.format(basealpha(cidx),cidy)
                tower = CellTower(cell_id, self, x, y, x+10, y+10)
                cidy += 1
                self.towers.append(tower)
            cidx += 1

    def add_person(self, person):
        person.world = self
        self.people.append(person)
        if person not in self.index[(person.x, person.y)]:
            self.index[(person.x,person.y)].append(person)
        self.notify_tower(person)

    def find_people_in_area(self, x1, y1, x2, y2):
        area = Area(x1, y1, x2, y2)
        return area.find_people(self)

    def notify_tower(self, person):
        for tower in self.towers:
            tower.handle_notification(person)
           
    def tick(self):

        for person in self.people:
            if person in self.index[(person.x, person.y)]:
                self.index[(person.x, person.y)].remove(person)
            person.tick()
            if person not in self.index[(person.x, person.y)]:
                self.index[person.x,person.y].append(person)

        self.time += 1

        day = int(self.time / DAY_SIZE)

        if self.time % DAY_SIZE == 0:

            ic_before = 0
            if self.infect_history:
                ic_before = self.infect_history[-1]['count']
            self.infect_rate_history.append({
                'time': day,
                'change': self.infected_count - ic_before
            })

            self.infect_history.append({
                'time': day,
                'count': self.infected_count
            })

    def rate_vectors(self):
        time_x = [i['time'] for i in self.infect_rate_history]
        infected_y = [i['change'] for i in self.infect_rate_history]

        return {
            'infected': {
                'x': time_x,
                'height': infected_y,
                'color': 'r'
            }
        }

    def cumulative_vectors(self):
        time_x = [i['time'] for i in self.infect_history]
        infected_y = [i['count'] for i in self.infect_history]

        return {
            'infected': {
                'x': time_x,
                'y1': infected_y,
                'color': 'r'
            }
        }

    def scatter_vectors(self):
        clean_x = []
        clean_y = []
        infected_x = []
        infected_y = []
        for p in self.people:
            if not p.infected:
                clean_x.append(p.x)
                clean_y.append(p.y)
            else:
                infected_x.append(p.x)
                infected_y.append(p.y)
        return {
            'infected': {
                'x': infected_x,
                'y': infected_y,
                's': 1,
                'color': 'r',
            },
            'clean': {
                'x': clean_x,
                'y': clean_y,
                's': 1,
                'color': 'b'
            }
        }


class Person(object):

    def __init__(self, personid):
        self.id = personid
        self.world = None
        self.x = random.randint(0, WORLD['width'] - 1)
        self.y = random.randint(0, WORLD['height'] - 1)
        self.infected = False
        self.vector = {'x':random.randint(-1,1), 'y': random.randint(-1,1)}
        self.steps = 0
        self.move_distance = random.randint(3,10)
        self.update_vector()

    def update_vector(self):
        if self.steps >= self.move_distance:
            self.vector['x'] = random.randint(-1,1)
            self.vector['y'] = random.randint(-1,1)

            # must always be moving
            if self.vector['x'] == 0 and self.vector['y'] == 0:
                return self.update_vector()

            self.steps = 0
            self.move_distance = random.randint(3,10)

        nextx = self.x + self.vector['x']
        nexty = self.y + self.vector['y']

        # corner tracking
        if nextx < 0:
            self.vector['x'] = random.randint(0,1)
        elif nextx >= WORLD['height']:
            self.vector['x'] = random.randint(-1,0)
        
        if nexty < 0:
            self.vector['y'] = random.randint(0,1)
        elif nexty >= WORLD['width']:
            self.vector['y'] = random.randint(-1,0)




    def tick(self):
        self.infect(self.world)
        self.x += self.vector['x']
        self.y += self.vector['y']
        self.steps += 1

        self.world.notify_tower(self)
        self.update_vector()

    def infect(self, world):
        if not self.infected:
            return

        for x in range((self.x - INFECT_RADIUS), (self.x + INFECT_RADIUS)):
            for y in range((self.y - INFECT_RADIUS), (self.y + INFECT_RADIUS)):
                people = world.index.get((x,y), [])

                for person in people:
                    if random.randint(0,100) >= (100*INFECT_PROBABILITY):
                        continue

                    if not person.infected:
                        person.infected = True
                        infect_log({'timestamp': world.time, 'source_person':
                            self.id, 'person': person.id})
                        world.infected_count += 1

class ScatterAnimation(object):

    def __init__(self, world):
        self.fig = plt.figure()
        self.world = world
        self.ax = self.fig.add_subplot(2,2,1)
        self.ax2 = self.fig.add_subplot(2,2,2)
        self.ax3 = self.fig.add_subplot(2,1,2)

        for tower in world.towers:
            patch = patches.Rectangle(
                    (tower.topleft['x'], tower.topleft['y']),
                    CELLSIZE, CELLSIZE,
                    linewidth=1,edgecolor='black', fill=False)
            self.ax.add_patch(patch)


        sv = world.scatter_vectors()
        self.scats = []
        self.cumulative_plots = []
        self.rate_plots = []
        for v in sv.values():
            self.scats.append(self.ax.scatter(**v))

        self.anim = FuncAnimation(self.fig, self.update, interval=100)
        
    def update(self, frame):
        if self.world.infected_count >= POPULATION:
            self.anim.event_source.stop()


        global TOWER_LOG
        global INFECT_LOG
        print('Computing T = %s' % self.world.time)
        self.world.tick()

        for scat in self.scats:
            scat.remove()

        for p in self.cumulative_plots:
            p.remove()

        for p in self.rate_plots:
            p.remove()

        self.cumulative_plots = []
        self.scats = []
        self.rate_plots = []

        sv = self.world.scatter_vectors()
        for v in sv.values():
            if v['x']:
                self.scats.append(self.ax.scatter(**v))

        cv = self.world.cumulative_vectors()
        for v in cv.values():
            self.cumulative_plots.append(self.ax2.fill_between(**v))

        rv = self.world.rate_vectors()
        for v in rv.values():
            self.rate_plots.append(self.ax3.bar(**v))

        with open('tower_log.txt','a') as f:
            f.writelines([(json.dumps(l) + '\n') for l in TOWER_LOG])
            TOWER_LOG=[]
        with open('infect_log.txt','a') as f:
            f.writelines([(json.dumps(l) + '\n') for l in INFECT_LOG])
            INFECT_LOG=[]

      




def main():
    global TOWER_LOG
    global INFECT_LOG

    if os.path.exists('tower_log.txt'):
        os.unlink('tower_log.txt')
        open('tower_log.txt','w').close()
    if os.path.exists('infect_log.txt'):
        os.unlink('infect_log.txt')
        open('infect_log.txt','w').close()

    world = World()
    for p in range(POPULATION):
        person = Person(p)
        if p == 1:
            person.infected=True
        world.add_person(person)

    anim = ScatterAnimation(world)

    plt.show()

    


if __name__ == '__main__':
    main()
