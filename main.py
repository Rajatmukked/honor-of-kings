import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image
import os, random

TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

GRID = 5
EMPTY_TILE = GRID * GRID - 1

def slice_image(image_path):
    img = Image.open(image_path)
    size = img.size[0] // GRID
    os.makedirs("pieces", exist_ok=True)

    idx = 0
    for y in range(GRID):
        for x in range(GRID):
            box = (x*size, y*size, (x+1)*size, (y+1)*size)
            img.crop(box).save(f"pieces/{idx}.png")
            idx += 1

def render_board(tiles):
    size = Image.open("pieces/0.png").size[0]
    board = Image.new("RGB", (size*GRID, size*GRID))

    for i, tile in enumerate(tiles):
        if tile == EMPTY_TILE:
            continue
        img = Image.open(f"pieces/{tile}.png")
        x = (i % GRID) * size
        y = (i // GRID) * size
        board.paste(img, (x, y))

    board.save("board.png")
    return "board.png"

class PuzzleView(discord.ui.View):
    def __init__(self, tiles):
        super().__init__(timeout=300)
        self.tiles = tiles
        self.empty = tiles.index(EMPTY_TILE)

    async def update(self, interaction):
        file = discord.File(render_board(self.tiles), filename="puzzle.png")
        await interaction.response.edit_message(attachments=[file], view=self)

    def move(self, delta, interaction):
        new = self.empty + delta
        if 0 <= new < GRID*GRID:
            self.tiles[self.empty], self.tiles[new] = self.tiles[new], self.tiles[self.empty]
            self.empty = new

    @discord.ui.button(label="⬆️", style=discord.ButtonStyle.primary)
    async def up(self, interaction, _):
        self.move(-GRID, interaction)
        await self.update(interaction)

    @discord.ui.button(label="⬇️", style=discord.ButtonStyle.primary)
    async def down(self, interaction, _):
        self.move(GRID, interaction)
        await self.update(interaction)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary)
    async def left(self, interaction, _):
        self.move(-1, interaction)
        await self.update(interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary)
    async def right(self, interaction, _):
        self.move(1, interaction)
        await self.update(interaction)

@bot.tree.command(name="puzzle")
async def puzzle(interaction: discord.Interaction):
    slice_image("puzzles/hok1.png")
    tiles = list(range(GRID*GRID))
    random.shuffle(tiles)

    view = PuzzleView(tiles)
    file = discord.File(render_board(tiles), filename="puzzle.png")

    await interaction.response.send_message(
        "🧩 **5×5 Puzzle – Move the tiles!**",
        file=file,
        view=view
    )

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
