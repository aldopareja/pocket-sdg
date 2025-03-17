import asyncio
import copy
import warnings

class AsyncNode:
    def __init__(self):
        self.successors = {}
    
    def add_successor(self,node,action="default"):
        if action in self.successors: 
            warnings.warn(f"Overwriting successor for action '{action}'")
        self.successors[action]=node
        return node
    
    def __rshift__(self,other): 
        return self.add_successor(other)
    
    def __sub__(self, action):
        assert isinstance(action, str)
        return _ConditionalTransition(self, action)
    
    async def exec(self, shared):
        pass
    
    async def run_async(self,shared): 
        if self.successors: 
            warnings.warn("Node won't run successors. Use AsyncFlow.")  
        return await self._run_async(shared)
    
    async def _run_async(self, shared):
        return await self.exec(shared)
    
class _ConditionalTransition:
    '''this is necessary so that `source - action >> target` conditionally connects source with target on a string of an action.'''
    def __init__(self,src,action): 
        self.src, self.action= src, action
    def __rshift__(self,tgt): 
        return self.src.add_successor(tgt,self.action)


class AsyncFlow(AsyncNode):
    def __init__(self, start):
        super().__init__()
        self.start = start

    def get_next_node(self,curr,action):
        nxt=curr.successors.get(action or "default")
        if not nxt and curr.successors: 
            warnings.warn(f"Flow ends: '{action}' not found in {list(curr.successors)}")
        return nxt

    async def _orch_async(self, shared):
        curr  = copy.copy(self.start)
        while curr:
            print(type(curr))
            c, shared = await curr._run_async(shared)
            curr = copy.copy(self.get_next_node(curr, c))
        return shared

    async def _run_async(self, shared):
        return await self._orch_async(shared)

