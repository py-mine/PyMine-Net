"""Contains packets related to crafting and recipes."""

from __future__ import annotations

from typing import Dict, List

from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket

__all__ = (
    "PlayCraftRecipeRequest",
    "PlaySetDisplayedRecipe",
    "PlaySetRecipeBookState",
    "PlayCraftRecipeResponse",
    "PlayDeclareRecipes",
    "PlayUnlockRecipes",
)


class PlayCraftRecipeRequest(ServerBoundPacket):
    """Sent when a client/player clicks a recipe in the crafting book that is craftable. (Client -> Server)

    :param int window_id: ID of the crafting table window.
    :param str recipe_identifier: The recipe identifier.
    :param bool make_all: Whether maximum amount that can be crafted is crafted.
    :ivar int id: Unique packet ID.
    :ivar window_id:
    :ivar recipe_identifier:
    :ivar make_all:
    """

    id = 0x18

    def __init__(self, window_id: int, recipe_identifier: str, make_all: bool):
        super().__init__()

        self.window_id = window_id
        self.recipe_identifier = recipe_identifier
        self.make_all = make_all

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayCraftRecipeRequest:
        return cls(buf.read("b"), buf.read_string(), buf.read("?"))


class PlaySetDisplayedRecipe(ServerBoundPacket):
    """Replaces Recipe Book Data, type 0. See here: https://wiki.vg/Protocol#Set_Displayed_Recipe (Client -> Server)

    :param str recipe_id: The identifier for the recipe.
    :ivar int id: Unique packet ID.
    :ivar recipe_id:
    """

    id = 0x1F

    def __init__(self, recipe_id: str):
        super().__init__()

        self.recipe_id = recipe_id

    @classmethod
    def unpack(cls, buf: Buffer) -> PlaySetDisplayedRecipe:
        return cls(buf.read_string())


class PlaySetRecipeBookState(ServerBoundPacket):
    """Replaces Recipe Book Data, type 1. See here: https://wiki.vg/Protocol#Set_Recipe_Book_State (Client -> Server)

    :param int book_id: One of the following: crafting (0), furnace (1), blast furnace (2), smoker (3).
    :param bool book_open: Whether the crafting book is open or not.
    :param bool filter_active: Unknown.
    :ivar int id: Unique packet ID.
    :ivar book_id:
    :ivar book_open:
    :ivar filter_active:
    """

    id = 0x1E

    def __init__(self, book_id: int, book_open: bool, filter_active: bool):
        super().__init__()

        self.book_id = book_id
        self.book_open = book_open
        self.filter_active = filter_active

    @classmethod
    def unpack(cls, buf: Buffer) -> PlaySetRecipeBookState:
        return cls(buf.read_varint(), buf.read("?"), buf.read("?"))


class PlayCraftRecipeResponse(ClientBoundPacket):
    """Response to a PlayCraftRecipeRequest, used to update the client's UI. (Server -> Client)

    :param int window_id: ID of the crafting table window.
    :param str recipe: The recipe identifier.
    :ivar int id: Unique packet ID.
    :ivar window_id:
    :ivar recipe:
    """

    id = 0x31

    def __init__(self, window_id: int, recipe_identifier: str):
        super().__init__()

        self.window_id = window_id
        self.recipe_identifier = recipe_identifier

    def pack(self) -> Buffer:
        return Buffer().write("b", self.window_id).write_string(self.recipe_identifier)


class PlayDeclareRecipes(ClientBoundPacket):
    """Sends all registered recipes to the client. (Server -> Client)

    :param Dict[str, dict] recipes: The recipes to be sent in the form {recipe_id: recipe_data}.
    :ivar int id: Unique packet ID.
    :ivar recipes:
    """

    id = 0x66

    def __init__(self, recipes: Dict[str, dict]):
        super().__init__()

        self.recipes = recipes

    def pack(self) -> Buffer:
        buf = Buffer()

        for recipe_id, recipe in self.recipes.items():
            buf.write_recipe(recipe_id, recipe)

        return buf


class PlayUnlockRecipes(ClientBoundPacket):
    """Unlocks specified locked recipes for the client. (Server -> Client)

    :param int action: The action to be taken, see here: https://wiki.vg/Protocol#Unlock_Recipes.
    :param bool crafting_book_open: If true, then the crafting recipe book will be open when the player opens its inventory.
    :param bool crafting_book_filter_active: If true, then the filtering option is active when the players opens its inventory.
    :param bool smelting_book_open: If true, then the smelting recipe book will be open when the player opens its inventory.
    :param bool smelting_book_filter_active: If true, then the filtering option is active when the players opens its inventory.
    :param bool blast_furnace_book_open: If true, then the blast furnace recipe book will be open when the player opens its inventory.
    :param bool blast_furnace_book_filter_active: If true, then the filtering option is active when the players opens its inventory.
    :param bool smoker_book_open: If true, then the smoker recipe book will be open when the player opens its inventory.
    :param bool smoker_book_filter_active: If true, then the filtering option is active when the players opens its inventory.
    :param List[str] recipe_ids_1: First list of recipe identifiers.
    :param Optional[List[str]] recipe_ids_2: Second list of recipe identifiers.
    :ivar int id: Unique packet ID.
    :ivar action:
    :ivar crafting_book_open:
    :ivar crafting_book_filter_active:
    :ivar smelting_book_open:
    :ivar smelting_book_filter_active:
    :ivar blast_furnace_book_open:
    :ivar blast_furnace_book_filter_active:
    :ivar smoker_book_open:
    :ivar smoker_book_filter_active:
    :ivar recipe_ids_1:
    :ivar recipe_ids_2:
    """

    id = 0x39

    def __init__(
        self,
        action: int,
        crafting_book_open: bool,
        crafting_book_filter_active: bool,
        smelting_book_open: bool,
        smelting_book_filter_active: bool,
        blast_furnace_book_open: bool,
        blast_furnace_book_filter_active: bool,
        smoker_book_open: bool,
        smoker_book_filter_active: bool,
        recipe_ids_1: List[str],
        recipe_ids_2: List[list] = None,
    ):
        super().__init__()

        self.action = action
        self.crafting_book_open = crafting_book_open
        self.crafting_book_filter_active = crafting_book_filter_active
        self.smelting_book_open = smelting_book_open
        self.smelting_book_filter_active = smelting_book_filter_active
        self.blast_furnace_book_open = blast_furnace_book_open
        self.blast_furnace_book_filter_active = blast_furnace_book_filter_active
        self.smoker_book_open = smoker_book_open
        self.smoker_book_filter_active = smoker_book_filter_active
        self.recipe_ids_1 = recipe_ids_1
        self.recipe_ids_2 = recipe_ids_2

    def pack(self) -> Buffer:
        buf = (
            Buffer()
            .write_varint(self.action)
            .write("?", self.crafting_book_open)
            .write("?", self.crafting_book_filter_active)
            .write("?", self.smelting_book_open)
            .write("?", self.smelting_book_filter_active)
            .write("?", self.blast_furnace_book_open)
            .write("?", self.blast_furnace_book_filter_active)
            .write("?", self.smoker_book_open)
            .write("?", self.smoker_book_filter_active)
            .write_varint(len(self.recipe_ids_1))
        )

        for recipe_id in self.recipe_ids_1:
            buf.write_string(recipe_id)

        if self.recipe_ids_2:
            buf.write("?", True)

            for recipe_id in self.recipe_ids_2:
                buf.write_string(recipe_id)
        else:
            buf.write("?", False)

        return buf
