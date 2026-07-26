import discord
from discord.ext import commands
import os
from threading import Thread
from flask import Flask

# --------------------------------------------------
# Render 24시간 방지용 가짜 웹서버 (Flask)
# --------------------------------------------------
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --------------------------------------------------
# 디스코드 봇 설정
# --------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 채널 ID
PANEL_CHANNEL_ID = 1529410158760034309
RESULT_CHANNEL_ID = 1530870174515724399

# --------------------------------------------------
# 자기소개 입력 팝업창 (Modal)
# --------------------------------------------------
class IntroModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="📝 자기소개 양식 작성")

        self.game_nickname = discord.ui.TextInput(
            label="🎮 인게임 닉네임",
            placeholder="예: 현이",
            max_length=15,
            required=True
        )
        
        self.user_id_num = discord.ui.TextInput(
            label="🔢 고유번호",
            placeholder="예: 227",
            max_length=10,
            required=True
        )
        
        self.age = discord.ui.TextInput(
            label="🎂 나이",
            placeholder="예: 20",
            max_length=3,
            required=True
        )

        self.play_time = discord.ui.TextInput(
            label="⏰ 접속 시간",
            style=discord.TextStyle.paragraph,
            placeholder="예: 평일 10:00 ~ 19:00 / 주말 09:00 ~ 00:00 (24시간제로 기재)",
            max_length=200,
            required=True
        )

        self.add_item(self.game_nickname)
        self.add_item(self.user_id_num)
        self.add_item(self.age)
        self.add_item(self.play_time)

    async def on_submit(self, interaction: discord.Interaction):
        result_channel = interaction.guild.get_channel(RESULT_CHANNEL_ID)
        
        if not result_channel:
            await interaction.response.send_message(
                "❌ 결과 채널을 찾을 수 없습니다.", 
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"✨ {interaction.user.display_name} 님의 프로필",
            description="서버에 새 멤버가 프로필을 등록했습니다!",
            color=discord.Color.from_rgb(0, 0, 0),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        embed.add_field(name="🎮 인게임 닉네임", value=f"`{self.game_nickname.value}`", inline=True)
        embed.add_field(name="🔢 고유번호", value=f"`{self.user_id_num.value}`", inline=True)
        embed.add_field(name="🎂 나이", value=f"`{self.age.value}`", inline=True)
        embed.add_field(name="⏰ 주요 접속 시간", value=f"```\n{self.play_time.value}\n```", inline=False)
        
        embed.set_footer(
            text=f"디스코드 태그: {interaction.user} | ID: {interaction.user.id}",
            icon_url=interaction.user.display_avatar.url
        )

        await result_channel.send(embed=embed)
        await interaction.response.send_message(
            f"✅ 프로필 작성이 완료되었습니다!", 
            ephemeral=True
        )

# --------------------------------------------------
# 영구 작동 패널 버튼 (View)
# --------------------------------------------------
class IntroPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="자기소개 작성하기", 
        style=discord.ButtonStyle.success, 
        emoji="📝", 
        custom_id="persistent_intro_button"
    )
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(IntroModal())

# --------------------------------------------------
# 봇 시작 시 실행
# --------------------------------------------------
@bot.event
async def on_ready():
    print(f"✅ 봇 로그인 성공: {bot.user.name}")
    bot.add_view(IntroPanelView())

    panel_channel = bot.get_channel(PANEL_CHANNEL_ID)
    if panel_channel:
        async for message in panel_channel.history(limit=5):
            if message.author == bot.user:
                await message.delete()

        panel_embed = discord.Embed(
            title="📋 서버 프로필 / 자기소개 등록",
            description=(
                "아래 **[📝 자기소개 작성하기]** 버튼을 눌러 양식을 작성해 주세요.\n"
                "제출된 자기소개는 퇴사후 1개월정도 보관됩니다.\n\n"
                "**📌 작성 항목**\n"
                "• **인게임 닉네임**\n"
                "• **고유번호**\n"
                "• **나이**\n"
                "• **접속 시간**"
            ),
            color=discord.Color.from_rgb(60, 0, 255)
        )
        panel_embed.set_footer(text="버튼을 누르면 작성 팝업창이 나타납니다. / 봇 오류 시 현 이(jiu_108) DM 주세요.")
        await panel_channel.send(embed=panel_embed, view=IntroPanelView())

# --------------------------------------------------
# 메인 실행부 (웹서버 + 봇 토큰)
# --------------------------------------------------
if __name__ == "__main__":
    keep_alive()  # 가짜 웹서버 시작
    bot.run(os.environ.get("DISCORD_TOKEN"))
