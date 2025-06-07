import pygame
import sys
import random
import time
import math

# pygameの初期化
pygame.init()
pygame.font.init()

# 画面サイズの設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hot Typing Action Game")

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# フォントの設定
title_font = pygame.font.SysFont(None, 128, bold=True, italic=True)  # 太字、斜体、サイズ2倍
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# 単語リストを外部ファイルから読み込む
def load_words_from_file(filename):
    """外部ファイルから単語リストを読み込む"""
    try:
        with open(filename, 'r') as file:
            # 空行や空白行を除外して単語リストを作成
            return [word.strip() for word in file.readlines() if word.strip()]
    except FileNotFoundError:
        print(f"警告: 単語リストファイル '{filename}' が見つかりません。デフォルトの単語リストを使用します。")
        # デフォルトの単語リスト（ファイルが見つからない場合のフォールバック）
        return [
            "python", "pygame", "programming", "keyboard", "computer", 
            "algorithm", "function", "variable", "developer", "software"
        ]

# 難易度別の単語リストを読み込む
words_short = load_words_from_file('words_short.txt')   # 3-5文字の単語
words_medium = load_words_from_file('words_medium.txt') # 6-10文字の単語
words_long = load_words_from_file('words_long.txt')     # 11-15文字の単語

# 現在の難易度レベル（0: 短い単語, 1: 中程度の単語, 2: 長い単語）
current_difficulty = 0

# キャラクター設定
class Character:
    def __init__(self, color=GREEN, is_player=True):
        self.radius = 15
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 7 if is_player else 3  # 敵は少し遅く
        self.color = color
        self.is_player = is_player
        
        # 敵キャラクター用の移動方向
        if not is_player:
            # ランダムな方向（-1.0〜1.0の範囲）
            self.dx = random.uniform(-1.0, 1.0)
            self.dy = random.uniform(-1.0, 1.0)
            # 方向ベクトルの正規化
            length = math.sqrt(self.dx**2 + self.dy**2)
            self.dx /= length
            self.dy /= length
    
    def move(self, dx, dy):
        if self.is_player:
            # プレイヤーキャラクターの移動（入力による）
            self.x = max(self.radius, min(WIDTH - self.radius, self.x + dx))
            self.y = max(self.radius, min(HEIGHT - self.radius, self.y + dy))
        else:
            # 敵キャラクターの移動（自動）
            new_x = self.x + self.dx * self.speed
            new_y = self.y + self.dy * self.speed
            
            # 壁での反射
            if new_x <= self.radius or new_x >= WIDTH - self.radius:
                self.dx *= -1
                new_x = self.x + self.dx * self.speed
            
            if new_y <= self.radius or new_y >= HEIGHT - self.radius:
                self.dy *= -1
                new_y = self.y + self.dy * self.speed
            
            self.x = new_x
            self.y = new_y
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def collides_with(self, other):
        """他のキャラクターとの衝突判定"""
        distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        return distance < (self.radius + other.radius)

# パーティクルクラス
class Particle:
    def __init__(self, x, y, color=WHITE):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.uniform(1, 3)
        self.speed = random.uniform(1, 3)
        angle = random.uniform(0, 2 * math.pi)  # ランダムな方向（0〜2π）
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.life = 100  # パーティクルの寿命（フレーム数）
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        
    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))
        
    def is_alive(self):
        return self.life > 0

# 敵の撃破エフェクト
class DeathEffect:
    def __init__(self, x, y, color=RED):
        self.x = x
        self.y = y
        self.original_y = y
        self.color = color
        self.radius = 15
        self.alpha = 255  # 完全に不透明から開始
        self.particles = []
        self.start_time = time.time()
        self.duration = 3.0  # エフェクト持続時間（秒）
        
        # パーティクルを生成
        for _ in range(20):  # 20個のパーティクルを生成
            self.particles.append(Particle(x, y))
            
    def update(self):
        # 経過時間の計算
        elapsed = time.time() - self.start_time
        progress = min(elapsed / self.duration, 1.0)  # 0.0〜1.0の進行度
        
        # アルファ値を更新（フェードアウト）
        self.alpha = int(255 * (1.0 - progress))
        
        # 徐々に下に移動
        self.y = self.original_y + (progress * 30)  # 3秒かけて30ピクセル下に移動
        
        # パーティクルの更新
        for particle in self.particles:
            particle.update()
            
    def draw(self):
        # 半透明の敵を描画
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.alpha), (self.radius, self.radius), self.radius)
        screen.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))
        
        # パーティクルを描画
        for particle in self.particles:
            particle.draw()
            
    def is_finished(self):
        return time.time() - self.start_time >= self.duration

# 敵の撃破エフェクトを作成する関数
def create_enemy_death_effect():
    """敵の撃破エフェクトを作成"""
    global enemy_active
    # 敵の現在位置でエフェクトを作成
    death_effects.append(DeathEffect(enemy.x, enemy.y))
    # 敵を非表示にする
    enemy_active = False

# キャラクターの初期化
player = Character(GREEN, True)
enemy = Character(RED, False)

# ゲーム変数
current_word = ""
typed_word = ""
score = 0
start_time = 0
end_time = None  # 終了時間を初期化
game_active = False
words_typed = 0
correct_words = 0
target_words = 15  # クリアに必要な正答数
player_health = 3  # プレイヤーの体力
last_hit_time = 0  # 最後にダメージを受けた時間
invincible_time = 3  # 無敵時間（秒）
enemy_active = True  # 敵キャラクターの有効状態
death_effects = []  # 敵の撃破エフェクトのリスト

# キー押下状態の管理
keys_pressed = {
    pygame.K_w: False,
    pygame.K_a: False,
    pygame.K_s: False,
    pygame.K_d: False
}

# ゲーム状態
STATE_MENU = 0
STATE_GAME = 1
STATE_RESULT = 2
STATE_CLEAR = 3  # クリア状態を追加
game_state = STATE_MENU

def get_new_word():
    """新しい単語をランダムに選択（難易度に応じて）"""
    global current_difficulty
    
    # 正答数に応じて難易度を設定
    if correct_words < 5:
        current_difficulty = 0  # 短い単語 (3-5文字)
        word_list = words_short
    elif correct_words < 10:
        current_difficulty = 1  # 中程度の単語 (6-10文字)
        word_list = words_medium
    else:
        current_difficulty = 2  # 長い単語 (11-15文字)
        word_list = words_long
    
    # 選択した難易度の単語リストからランダムに選択
    if word_list:
        return random.choice(word_list)
    else:
        # 単語リストが空の場合のフォールバック
        return "fallback"

def reset_game():
    """ゲームをリセット"""
    global current_word, typed_word, score, start_time, game_active, words_typed, correct_words
    global player, enemy, player_health, last_hit_time, enemy_active, end_time
    global words_short, words_medium, words_long, current_difficulty, death_effects
    
    # 単語リストを再読み込み（単語ファイルが更新された場合に反映される）
    words_short = load_words_from_file('words_short.txt')
    words_medium = load_words_from_file('words_medium.txt')
    words_long = load_words_from_file('words_long.txt')
    current_difficulty = 0  # 難易度をリセット
    
    current_word = get_new_word()
    typed_word = ""
    score = 0
    start_time = time.time()
    end_time = None  # 終了時間をリセット
    game_active = True
    words_typed = 0
    correct_words = 0
    player_health = 3
    last_hit_time = 0
    enemy_active = True
    death_effects = []  # エフェクトをリセット
    
    # キャラクターのリセット
    player = Character(GREEN, True)
    enemy = Character(RED, False)

def draw_menu():
    """メニュー画面の描画"""
    screen.fill(BLACK)
    
    # タイトル
    title_text1 = title_font.render("Hot Typing", True, ORANGE)
    title_text2 = title_font.render("Action Game", True, ORANGE)
    screen.blit(title_text1, (WIDTH//2 - title_text1.get_width()//2, 120))
    screen.blit(title_text2, (WIDTH//2 - title_text2.get_width()//2, 200))
    
    # 説明
    instruction_text = font.render("Press SPACE to start", True, WHITE)
    screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, 300))
    
    # 操作説明
    control_text = small_font.render("Controls: W (up), A (left), S (down), D (right)", True, WHITE)
    screen.blit(control_text, (WIDTH//2 - control_text.get_width()//2, 350))
    
    # ゲームルール説明
    rule1 = small_font.render("Type 15 words correctly to win!", True, WHITE)
    rule2 = small_font.render("Avoid the red enemy or lose health!", True, WHITE)
    rule3 = small_font.render("You have 3 health points. After being hit, you're invincible for 3 seconds.", True, WHITE)
    
    screen.blit(rule1, (WIDTH//2 - rule1.get_width()//2, 400))
    screen.blit(rule2, (WIDTH//2 - rule2.get_width()//2, 425))
    screen.blit(rule3, (WIDTH//2 - rule3.get_width()//2, 450))

def draw_game():
    """ゲーム画面の描画"""
    screen.fill(BLACK)
    
    # 進捗表示（正答数/目標数）
    progress_text = font.render(f"Words: {correct_words}/{target_words}", True, WHITE)
    screen.blit(progress_text, (20, 20))
    
    # スコア
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH - score_text.get_width() - 20, 20))
    
    # 体力表示
    for i in range(player_health):
        pygame.draw.circle(screen, GREEN, (30 + i * 30, 60), 10)
    
    # 無敵状態の表示
    current_time = time.time()
    if current_time - last_hit_time < invincible_time:
        invincible_text = small_font.render("INVINCIBLE!", True, YELLOW)
        screen.blit(invincible_text, (30, 80))
    
    # 敵キャラクターの描画（有効な場合のみ）
    if enemy_active:
        enemy.draw()
    
    # 敵の撃破エフェクトの描画
    for effect in death_effects[:]:
        effect.update()
        effect.draw()
        if effect.is_finished():
            death_effects.remove(effect)
    
    # プレイヤーキャラクターの描画
    player.draw()
    
    # 単語表示エリアの背景（半透明）
    word_area_y = 200
    word_text = font.render(current_word, True, WHITE)
    word_area_width = max(300, word_text.get_width() + 40)
    word_area_height = 100
    
    # 半透明の背景を描画
    s = pygame.Surface((word_area_width, word_area_height))
    s.set_alpha(180)
    s.fill((20, 20, 40))
    screen.blit(s, (WIDTH//2 - word_area_width//2, word_area_y - 10))
    
    # 現在の単語（タイプすべき単語）
    screen.blit(word_text, (WIDTH//2 - word_text.get_width()//2, word_area_y))
    
    # タイプ中の単語
    typed_color = GREEN if typed_word == current_word[:len(typed_word)] else RED
    typed_text = font.render(typed_word, True, typed_color)
    screen.blit(typed_text, (WIDTH//2 - word_text.get_width()//2, word_area_y + 40))
    
    # 進捗バー（減っていくように変更）
    remaining_words = target_words - correct_words
    progress_width = int((remaining_words / target_words) * (WIDTH - 40))
    pygame.draw.rect(screen, BLUE, (20, HEIGHT - 40, WIDTH - 40, 20), 2)
    pygame.draw.rect(screen, BLUE, (20, HEIGHT - 40, progress_width, 20))

def draw_results(is_clear=False):
    """結果画面の描画"""
    global end_time
    screen.fill(BLACK)
    
    # 結果タイトル
    if is_clear:
        result_title = title_font.render("Game Clear!", True, GREEN)
    else:
        result_title = title_font.render("Game Over", True, RED)
    
    screen.blit(result_title, (WIDTH//2 - result_title.get_width()//2, 100))
    
    # スコア
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 200))
    
    # 統計
    # クリア時またはゲームオーバー時の時間を使用（タイマーを止める）
    if end_time is None:
        end_time = time.time()
    
    elapsed_time = end_time - start_time
    minutes = elapsed_time / 60
    wpm = int(correct_words / max(1, minutes))
    accuracy = int((correct_words / max(1, words_typed)) * 100)
    
    time_text = font.render(f"Time: {int(elapsed_time)} seconds", True, WHITE)
    screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, 250))
    
    wpm_text = font.render(f"Words Per Minute: {wpm}", True, WHITE)
    screen.blit(wpm_text, (WIDTH//2 - wpm_text.get_width()//2, 300))
    
    accuracy_text = font.render(f"Accuracy: {accuracy}%", True, WHITE)
    screen.blit(accuracy_text, (WIDTH//2 - accuracy_text.get_width()//2, 350))
    
    # 再開指示
    restart_text = font.render("Press SPACE to play again", True, WHITE)
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 450))

def update_character_position():
    """キャラクターの位置を更新"""
    # プレイヤーキャラクターの移動
    dx, dy = 0, 0
    if keys_pressed[pygame.K_w]:
        dy -= player.speed
    if keys_pressed[pygame.K_s]:
        dy += player.speed
    if keys_pressed[pygame.K_a]:
        dx -= player.speed
    if keys_pressed[pygame.K_d]:
        dx += player.speed
    
    # 斜め移動の速度を調整（ノーマライズ）
    if dx != 0 and dy != 0:
        dx *= 0.7071  # 1/sqrt(2)
        dy *= 0.7071
        
    player.move(dx, dy)
    
    # 敵キャラクターの移動（有効な場合のみ）
    if enemy_active:
        enemy.move(0, 0)  # 引数は使用されない（自動移動）
        
        # 衝突判定
        current_time = time.time()
        if player.collides_with(enemy) and current_time - last_hit_time >= invincible_time:
            handle_collision()

def handle_collision():
    """衝突時の処理"""
    global player_health, last_hit_time, game_active, game_state, end_time
    
    player_health -= 1
    last_hit_time = time.time()
    
    # 体力がなくなったらゲームオーバー
    if player_health <= 0:
        game_active = False
        game_state = STATE_RESULT
        end_time = time.time()  # タイマーを停止

# ゲームループ
clock = pygame.time.Clock()
running = True
FPS = 120

# カスタムイベント定義
ENEMY_RESPAWN_EVENT = pygame.USEREVENT + 1

while running:
    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            # WASDキーの状態を更新
            if event.key in keys_pressed:
                keys_pressed[event.key] = True
                
            if game_state == STATE_MENU:
                if event.key == pygame.K_SPACE:
                    game_state = STATE_GAME
                    reset_game()
                    
            elif game_state == STATE_GAME and game_active:
                if event.key == pygame.K_RETURN:
                    # 単語の確認
                    words_typed += 1
                    if typed_word == current_word:
                        score += len(current_word)
                        correct_words += 1
                        
                        # 敵の撃破エフェクトを作成
                        create_enemy_death_effect()
                        
                        # 目標達成チェック
                        if correct_words >= target_words:
                            game_active = False
                            game_state = STATE_CLEAR
                            # タイマーを停止するために終了時間を記録
                            end_time = time.time()
                        else:
                            # 3秒後に新しい敵を出現させる
                            pygame.time.set_timer(ENEMY_RESPAWN_EVENT, 3000, True)
                            current_word = get_new_word()
                            typed_word = ""
                    else:
                        # 不正解の場合は次の単語へ
                        current_word = get_new_word()
                        typed_word = ""
                    
                elif event.key == pygame.K_BACKSPACE:
                    # 一文字削除
                    typed_word = typed_word[:-1]
                    
                elif event.key == pygame.K_ESCAPE:
                    # ゲーム中断
                    game_state = STATE_MENU
                    
                elif event.unicode.isalpha():
                    # すべてのアルファベットキー（WASDを含む）を受け付ける
                    next_char = event.unicode.lower()
                    
                    # 次に入力すべき文字が正しい場合のみ受け付ける
                    if len(typed_word) < len(current_word) and next_char == current_word[len(typed_word)]:
                        typed_word += next_char
                        
                        # 正しい文字列が入力されたら自動的に確定する
                        if typed_word == current_word:
                            words_typed += 1
                            score += len(current_word)
                            correct_words += 1
                            
                            # 敵の撃破エフェクトを作成
                            create_enemy_death_effect()
                            
                            # 目標達成チェック
                            if correct_words >= target_words:
                                game_active = False
                                game_state = STATE_CLEAR
                                # タイマーを停止するために終了時間を記録
                                end_time = time.time()
                            else:
                                # 3秒後に新しい敵を出現させる
                                pygame.time.set_timer(ENEMY_RESPAWN_EVENT, 3000, True)
                                current_word = get_new_word()
                                typed_word = ""
                    
            elif game_state == STATE_RESULT or game_state == STATE_CLEAR:
                if event.key == pygame.K_SPACE:
                    game_state = STATE_GAME
                    reset_game()
                    
        elif event.type == pygame.KEYUP:
            # WASDキーの状態を更新
            if event.key in keys_pressed:
                keys_pressed[event.key] = False
                
        elif event.type == ENEMY_RESPAWN_EVENT:
            # 敵キャラクターを再出現させる
            enemy = Character(RED, False)
            enemy_active = True
    
    # キャラクターの更新（ゲーム中のみ）
    if game_state == STATE_GAME and game_active:
        update_character_position()
    
    # 描画
    if game_state == STATE_MENU:
        draw_menu()
        
    elif game_state == STATE_GAME:
        draw_game()
        
    elif game_state == STATE_RESULT:
        draw_results(False)  # ゲームオーバー
        
    elif game_state == STATE_CLEAR:
        draw_results(True)  # ゲームクリア
    
    # 画面更新
    pygame.display.flip()
    clock.tick(FPS)

# pygameの終了
pygame.quit()
sys.exit()
