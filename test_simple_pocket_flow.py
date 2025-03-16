import asyncio
import aiohttp
from simple_pocket_flow import AsyncFlow, AsyncNode

async def async_call_llm(prompt):
    messages = [
        {
            "role": "user",
            "content": prompt
        },
    ]
    request_data = {
        "model": "phi4-mini",
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.8,
        "stream": False
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/v1/chat/completions",
            json=request_data,
            headers={'Content-Type': 'application/json'},
            timeout=aiohttp.ClientTimeout(total=120)
        ) as response:
            r = await response.json()
            response = [choice["message"]["content"] for choice in r["choices"]][0]
        return response

class AsyncGuesser(AsyncNode):
    async def exec(self, shared):
        hint = await shared["guesser_queue"].get()
        past_guesses = shared.get("past_guesses", [])
        prompt = f"Given hint: {hint}, past wrong guesses: {past_guesses}, make a new guess. Directly reply a single word:"
        guess = await async_call_llm(prompt)
        print(f"Guesser: I guess it's - {guess}")
        
        if guess.lower() == shared["target_word"].lower():
            print("Game Over - Correct Guess!!")
            await shared["hinter_queue"].put("GAME OVER")
            return "end"
        
        if "past_guesses" not in shared:
            shared["past_guesses"] = []
        
        shared["past_guesses"].append(guess)

        await shared["hinter_queue"].put(guess)
        return "continue"
    
class AsyncHinter(AsyncNode):
    async def exec(self, shared):
        guess = await shared["hinter_queue"].get()
        if guess == "GAME OVER":
            return "end"
        
        target = shared["target_word"]
        forbidden = shared["forbidden_words"]
        past_guesses = shared.get("past_guesses", [])

        prompt = f"Generate hint for '{target}'\nForbidden words: {forbidden}"
        if past_guesses:
            prompt += f"\nPrevious wrong guesses: {past_guesses}\nMake hint more specific."
        
        prompt += "\nUse at most 5 words."

        hint  = await async_call_llm(prompt)
        print(f"\nHinter: Here's your hint - {hint}")
        await shared["guesser_queue"].put(hint)
        return "continue"

async def main():
    # Set up game
    shared = {
        "target_word": "nostalgia",
        "forbidden_words": ["memory", "past", "remember", "feeling", "longing"],
        "hinter_queue": asyncio.Queue(),
        "guesser_queue": asyncio.Queue()
    }
    
    print("Game starting!")
    print(f"Target word: {shared['target_word']}")
    print(f"Forbidden words: {shared['forbidden_words']}")

    # Initialize by sending empty guess to hinter
    await shared["hinter_queue"].put("")

    # Create nodes and flows
    hinter = AsyncHinter()
    guesser = AsyncGuesser()

    # Set up flows
    hinter_flow = AsyncFlow(start=hinter)
    guesser_flow = AsyncFlow(start=guesser)

    # Connect nodes to themselves
    hinter - "continue" >> hinter
    guesser - "continue" >> guesser

    # Run both agents concurrently
    await asyncio.gather(
        hinter_flow.run_async(shared),
        guesser_flow.run_async(shared)
    )

asyncio.run(main())