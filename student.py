# Guilherme Rosa - 113968
# Rui Machado - 113765
# Henrique Teixeira 114588
from layers.FoodDetectionLayer import FoodDetectionLayer
from sensory_process import InternalState, SensorialProcess
from layers.SurvivalLayer import SurvivalLayer
from state_machine import StateMachine
import websockets
import asyncio
import json
import os
import getpass
from proto import Key
from states.ChaseFood import ChaseFood
from states.Idle import Idle
from typing import List, Tuple
from states.WanderWithGridDivision import WanderWithGridDivision
from layers.WanderLayer import WanderLayer
from states.Swerve import Swerve


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    # init internal state with empty food list and set states
    internal_state = InternalState()
    internal_state.set_states(
        [Idle(), ChaseFood(), WanderWithGridDivision(), Swerve()]
    )
    initial_state = internal_state.get_states()[0]

    # init sensorial process
    sensorial_process = SensorialProcess(
        [WanderLayer(), FoodDetectionLayer(), SurvivalLayer()], internal_state
    )

    # init state machine
    state_machine = StateMachine(initial_state)
    internal_state.current_state = initial_state

    try:
        async with websockets.connect(f"ws://{server_address}/player") as websocket:
            await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
            print("Connected to server.")

            is_first = True
            while True:
                try:
                    world = json.loads(await websocket.recv())
                    # Ensure map exists with default values
                    world.setdefault("map", [[0] * 24 for _ in range(48)])
                    world.setdefault("body", [[0, 0]])
                    world.setdefault("sight", {})

                    if is_first:
                        is_first = False
                        initial_foods = find_all_food(world["map"])
                        internal_state.set_foods(initial_foods)
                        internal_state.set_map(world["map"])

                    if is_multiplayer(world):
                        internal_state.traverse = False

                    processed_world = sensorial_process.process_world(world)
                    response = state_machine.tick_machine(processed_world)

                    if response is not None:
                        await send_command(websocket, response)
                    else:
                        await send_command(websocket, Key(Key.EMPTY))

                    await asyncio.sleep(0.05)

                except websockets.exceptions.ConnectionClosed as e:
                    print(f"WebSocket connection closed: {e}")
                    break
    except Exception as e:
        print(f"Error in agent_loop: {e}")
        import traceback

        traceback.print_exc()


def find_all_food(grid) -> List[Tuple[int, int]]:
    """Find all food positions in the grid."""
    food_positions = []
    if grid:
        for y in range(len(grid[0])):
            for x in range(len(grid)):
                if grid[x][y] == 2:
                    food_positions.append((x, y))
    print(f"Found food at positions: {food_positions}")
    return food_positions or []


async def send_command(websocket, key: Key):
    try:
        if key and key.value:
            await websocket.send(json.dumps({"cmd": "key", "key": key.value}))
    except Exception as e:
        print(f"Error in send_command: {e}")


def is_multiplayer(world):
    if world.get("players", None) is not None:
        if len(world["players"]) > 1:
            return True
    return False


# DO NOT CHANGE THE LINES BELOW
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
