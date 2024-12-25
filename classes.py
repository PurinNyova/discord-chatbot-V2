from sql import Cache, Persona, engine
from typing import Union
from sqlalchemy.orm import sessionmaker
import ast

class BaseManager:
    def __init__(self, origin, tableClass):
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()
        self.tableClass = tableClass
        self.data: Union[Cache, Persona] = self.session.query(tableClass).filter_by(origin=origin).first()
        if self.data is None:
            self.createData(origin)
    def __del__(self):
        self.session.close()
        print(f"{self.tableClass} Manager object is being deleted.")
    
    def createData(self, origin):
        raise NotImplementedError("Subclass must implement")

    def change_data(self, other=None, delete=False, modify=False):
        object = self.data if other is None else other
              # Modify the string (if needed)
        if delete:
            self.session.delete(object)
        elif not modify:
            self.session.add(object)
        self.session.commit()
        self.session.close()


    def endecoder(self, obj) -> Union[list, dict, str]:
        if isinstance(obj, list) or isinstance(obj, dict):
            return str(obj)
        elif isinstance(obj, str):
            return ast.literal_eval(obj)

class CacheManager(BaseManager):
    def __init__(self, origin):
        super().__init__(origin, Cache)
        self.globalChatTask: dict = self.endecoder(self.data.globalChatTask)
        self.activeSession: list = self.endecoder(self.data.activeSessions)

    def createData(self, origin):
        cache_record = Cache(
                origin=origin,
                activeSessions="[]",
                globalChatTask="{}",
                activeModel = "1",
                requireReply = False,
            )
        self.change_data(cache_record)
        self.data = self.session.query(Cache).filter_by(origin=origin).first()
    def updateGlobalChatTask(self):
        self.data.globalChatTask = self.endecoder(self.globalChatTask)
        self.change_data()
    def updateActiveSession(self):
        self.data.activeSessions = self.endecoder(self.activeSession)
        self.change_data()

class PersonalityManager(BaseManager):
    def __init__(self, origin):
        self.origin = origin
        super().__init__(origin, Persona)
    
    def addPersonality(self, name:str, profile:str, personality:str):
        personality_record = Persona(
            origin=self.origin,
            name=name,
            profilePicture=profile,
            personality=personality,
        )
        self.change_data(personality_record)
        self.data = self.session.query(Persona).filter_by(origin=self.origin, name=name).first()
    
    def modifyPersonality(self, name: str, profile: str, personality: str):
        personality_record = Persona(
            origin=self.origin,
            name=name,
            profilePicture=profile,
            personality=personality
        )
        self.data = personality_record
        self.change_data(modify=True)
    
    def returnPersonas(self, personaObject=False) -> Union[list[Persona], list]: #Returns a list of all persona in a server
        self.data = self.session.query(Persona).filter_by(origin=self.origin).all()
        return self.data if personaObject else list(map(lambda persona: persona.name, self.data))
    
    def getPersona(self, name): #Loads desired persona data in register
        self.data = self.session.query(Persona).filter_by(origin=self.origin, name=name).first()

    def createData(self, origin):
        pass