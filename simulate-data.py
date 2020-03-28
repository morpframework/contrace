import random
import time
import os
import json

WORLD = {
    'width': 30,
    'height': 30
}

POPULATION = 40
CYCLES = 100
CELLSIZE = 5

def tower_log(payload, filename='tower_log.txt'):
    with open(filename,'a') as f:
        f.write(json.dumps(payload) + '\n')

def infect_log(payload, filename='infect_log.txt'):
    with open(filename,'a') as f:
        f.write(json.dumps(payload) + '\n')

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
    
    def __init__(self, cellid, *args, **kwargs):
        self.id = cellid
        super().__init__(*args, **kwargs)
        self.people = []

    def handle_notification(self, person):
        incell = self.contains(person.x, person.y)
        if incell and person in self.people:
            return

        if incell and person not in self.people:
            self.people.append(person)
            tower_log({'timestamp': int(time.time()), 'cell_id': self.id, 'event':
                'Enter Cell', 'person_id': person.id})

        if not incell and person in self.people:
            self.people.remove(person)
            tower_log({'timestamp': int(time.time()), 'cell_id': self.id, 'event':
                'Leave Cell', 'person_id': person.id})





class World(object):

    def __init__(self, width=WORLD['width'], height=WORLD['height']):
        self.width = width
        self.height = height
        self.people = []
        self.towers = []
        cidx = 65
        for x in range(0, width, CELLSIZE):
            cidy = 0
            for y in range(0, height, CELLSIZE):
                cell_id = '{}{}'.format(chr(cidx),cidy)
                tower = CellTower(cell_id, x, y, x+10, y+10)
                cidy += 1
                self.towers.append(tower)
            cidx += 1

    def add_person(self, person):
        person.world = self
        self.people.append(person)
        self.notify_tower(person)

    def find_people_in_area(self, x1, y1, x2, y2):
        area = Area(x1, y1, x2, y2)
        return area.find_people(self)

    def notify_tower(self, person):
        for tower in self.towers:
            tower.handle_notification(person)
           
    def tick(self):
        for person in self.people:
            person.tick()

    def display(self):
        infected = list([i for i in self.people if
            i.infected])
        infected_count = len(infected)
        population_count = len(self.people)
        clean_count = population_count - infected_count
        print('Population = %s' % population_count)
        print('Infected = %s' % infected_count)
        print('Clean = %s' % clean_count)
        for y in range(-1,self.height+2):
            for x in range(-1,self.width+2):
                if y == -1 and x == -1:
                    print('+', end='')
                if y == -1 and x > -1:
                    print('+', end='')
                if y > -1 and x == -1:
                    print('+', end='')
                if y == -1:
                    continue
                if x == -1:
                    continue


                if y == self.height+1 and x == self.width+1:
                    print('+',end='')
                    continue

                if y == self.height+1 and x < self.width+1:
                    print('+', end='')
                    continue

                if y <= self.height+1 and x == self.width+1:
                    print('+', end='')
                    continue



                people_in_location = []
                for person in self.people:
                    person.infect(self)
                    if person.x == x and person.y == y:
                        people_in_location.append(person)
                if people_in_location:
                    has_infected = False
                    for p in people_in_location:
                        if p.infected:
                            has_infected = True
                    if has_infected:
                        print('Z', end='')
                    else:
                        print('X', end='')
                else:
                    print(' ', end='')
            print('')
        
class Person(object):

    def __init__(self, personid):
        self.id = personid
        self.world = None
        self.x = random.randint(0, WORLD['width'])
        self.y = random.randint(0, WORLD['height'])
        self.infected = False
        self.vector = {'x':random.randint(-1,1), 'y': random.randint(-1,1)}
        self.update_vector()

    def update_vector(self):
        nextx = self.x + self.vector['x']
        nexty = self.y + self.vector['y']
        if nextx < 0:
            self.vector['x'] = random.randint(0,1)
        elif nextx > WORLD['height']:
            self.vector['x'] = random.randint(-1,0)
        
        if nexty < 0:
            self.vector['y'] = random.randint(0,1)
        elif nexty > WORLD['width']:
            self.vector['y'] = random.randint(-1,0)

        if self.vector['x'] == 0 and self.vector['y'] == 0:
            # must always be moving
            self.vector['x'] = random.sample([-1,1],1)[0]
            self.vector['y'] = random.sample([-1,1],1)[0]

    def tick(self):
        self.x += self.vector['x']
        self.y += self.vector['y']
        self.world.notify_tower(self)
        self.update_vector()

    def infect(self, world):
        if not self.infected:
            return

        for person in world.people:
            if (((self.x - 1) <= person.x) and ((self.y - 1) <= person.y) and 
                    (person.x <= (self.x + 1)) and (person.y <= (self.y + 1))):
                if not person.infected:
                    person.infected = True
                    infect_log({'timestamp': int(time.time()), 'source_person':
                        self.id, 'person': person.id})


def main():
    world = World()
    for p in range(POPULATION):
        person = Person(p)
        if p == 1:
            person.infected=True
        world.add_person(person)

    for c in range(CYCLES):
        world.tick()
        os.system('clear')
        print('T = %s' % c)
        world.display()
        if len(list([i for i in world.people if i.infected])) >= POPULATION:
            break
        time.sleep(1)


if __name__ == '__main__':
    main()
