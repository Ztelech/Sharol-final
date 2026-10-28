import pygame
import sys
import random

# --- INICIALIZACIÓN ---
pygame.init()
pygame.font.init()

# --- CONSTANTES ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# Colores
COLOR_BG = (173, 216, 230)      # Azul cielo
COLOR_HEART = (255, 20, 60)     # Rojo Pasión
COLOR_PIPE = (144, 238, 144)    # Verde
COLOR_PIPE_BORDER = (34, 139, 34)
COLOR_TEXT = (255, 255, 255)
COLOR_BTN = (255, 255, 255)
COLOR_VICTORY_BG = (255, 182, 193) # Rosa pastel

# Configuración de pantalla
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Coldy Game: Para mi jugadora favorita")
clock = pygame.time.Clock()

# --- FUENTES (Con respaldo por si fallan) ---
def get_font(name, size, bold=False):
    try:
        return pygame.font.SysFont(name, size, bold=bold)
    except:
        return pygame.font.Font(None, size)

FONT_MAIN = get_font('Arial', 24, bold=True)
FONT_TITLE = get_font('Comic Sans MS', 40, bold=True)
FONT_VICTORY = get_font('Arial', 20, bold=True)

# --- CLASES ---

class Heart:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.vel = 0
        self.gravity = 0.5
        self.lift = -8
        self.rect = pygame.Rect(self.x, self.y, 30, 30)

    def jump(self):
        self.vel = self.lift

    def update(self):
        self.vel += self.gravity
        self.y += self.vel
        self.rect.y = int(self.y)
        
        if self.y > SCREEN_HEIGHT or self.y < 0:
            return True # Chocó suelo/techo
        return False

    def draw(self, surface):
        # Dibujo procedimental del corazón (No requiere imagen png)
        cx, cy = self.rect.centerx, self.rect.centery
        # Lóbulo izquierdo
        pygame.draw.circle(surface, COLOR_HEART, (cx - 7, cy - 5), 9)
        # Lóbulo derecho
        pygame.draw.circle(surface, COLOR_HEART, (cx + 7, cy - 5), 9)
        # Triángulo abajo
        points = [(cx - 16, cy - 2), (cx + 16, cy - 2), (cx, cy + 15)]
        pygame.draw.polygon(surface, COLOR_HEART, points)

class Pipe:
    def __init__(self, x, gap_y, gap_size, speed):
        self.x = x
        self.width = 50
        self.gap_y = gap_y
        self.gap_size = gap_size
        self.speed = speed
        self.passed = False
        self.top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        self.bot_rect = pygame.Rect(self.x, self.gap_y + self.gap_size, self.width, SCREEN_HEIGHT - (self.gap_y + self.gap_size))

    def update(self):
        self.x -= self.speed
        self.top_rect.x = self.x
        self.bot_rect.x = self.x

    def draw(self, surface):
        # Tubo superior
        pygame.draw.rect(surface, COLOR_PIPE, self.top_rect)
        pygame.draw.rect(surface, COLOR_PIPE_BORDER, self.top_rect, 3)
        # Tubo inferior
        pygame.draw.rect(surface, COLOR_PIPE, self.bot_rect)
        pygame.draw.rect(surface, COLOR_PIPE_BORDER, self.bot_rect, 3)

    def collide(self, player_rect):
        return self.top_rect.colliderect(player_rect) or self.bot_rect.colliderect(player_rect)

class Button:
    def __init__(self, text, x, y, w, h, action_code):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action_code = action_code
        self.hover = False

    def draw(self, surface):
        col = (230, 230, 230) if self.hover else COLOR_BTN
        pygame.draw.rect(surface, col, self.rect, border_radius=10)
        pygame.draw.rect(surface, (0,0,0), self.rect, 2, border_radius=10)
        
        txt = FONT_MAIN.render(self.text, True, (0,0,0))
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

# --- FUNCIONES DE TEXTO ---
def draw_text_centered(surface, text, font, color, y_off):
    # Sombra
    shad = font.render(text, True, (100,100,100))
    surface.blit(shad, shad.get_rect(center=(SCREEN_WIDTH//2 + 2, SCREEN_HEIGHT//2 + y_off + 2)))
    # Texto
    txt = font.render(text, True, color)
    surface.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + y_off)))

def wrap_text(surface, text, font, color, rect):
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        fw, fh = font.size(' '.join(current_line))
        if fw > rect.width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))

    y = rect.y
    for line in lines:
        if y < rect.bottom:
            t = font.render(line, True, color)
            surface.blit(t, t.get_rect(center=(rect.centerx, y)))
            y += font.get_height() + 5

# --- BUCLE PRINCIPAL ---
def main():
    STATE_MENU = 0
    STATE_PLAY = 1
    STATE_GAMEOVER = 2
    STATE_VICTORY = 3
    
    state = STATE_MENU
    
    # Dificultades: [hueco, velocidad, frecuencia, meta]
    diffs = {
        'F': {'gap': 170, 'spd': 3, 'freq': 120, 'goal': 10},
        'M': {'gap': 150, 'spd': 4, 'freq': 100, 'goal': 15},
        'D': {'gap': 130, 'spd': 5, 'freq': 90, 'goal': 20}
    }
    cur_diff = 'M'
    
    heart = Heart()
    pipes = []
    score = 0
    frames = 0
    
    # Variable para el tiempo de seguridad en la victoria
    victory_timer = 0 
    
    btns = [
        Button("Fácil (10 pts)", 100, 250, 200, 50, 'F'),
        Button("Medio (15 pts)", 100, 320, 200, 50, 'M'),
        Button("Difícil (20 pts)", 100, 390, 200, 50, 'D')
    ]

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(COLOR_BG)
        
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                if state == STATE_MENU:
                    for b in btns:
                        if b.rect.collidepoint(e.pos):
                            cur_diff = b.action_code
                            state = STATE_PLAY
                            heart = Heart()
                            pipes = []
                            score = 0
                            frames = 0
                elif state == STATE_PLAY:
                    heart.jump()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    if state == STATE_PLAY: 
                        heart.jump()
                    elif state == STATE_GAMEOVER: 
                        state = STATE_MENU
                    elif state == STATE_VICTORY: 
                        # SOLO permite salir si han pasado 3000 ms (3 segundos)
                        current_time = pygame.time.get_ticks()
                        if current_time - victory_timer > 3000:
                            state = STATE_MENU

        # Lógica
        if state == STATE_MENU:
            draw_text_centered(screen, "Coldy Game", FONT_TITLE, (255,255,255), -150)
            draw_text_centered(screen, "Selecciona Dificultad", FONT_MAIN, (50,50,50), -80)
            m_pos = pygame.mouse.get_pos()
            for b in btns:
                b.update(m_pos)
                b.draw(screen)

        elif state == STATE_PLAY:
            frames += 1
            cfg = diffs[cur_diff]
            
            if frames % cfg['freq'] == 0:
                gy = random.randint(50, SCREEN_HEIGHT - 50 - cfg['gap'])
                pipes.append(Pipe(SCREEN_WIDTH, gy, cfg['gap'], cfg['spd']))

            for p in pipes[:]:
                p.update()
                p.draw(screen)
                if p.x + p.width < 0: pipes.remove(p)
                if not p.passed and p.x < heart.rect.x:
                    score += 1
                    p.passed = True
                if p.collide(heart.rect): state = STATE_GAMEOVER

            if heart.update(): state = STATE_GAMEOVER
            heart.draw(screen)
            
            # HUD
            sc_txt = FONT_MAIN.render(f"Puntos: {score} / {cfg['goal']}", True, (255,255,255))
            screen.blit(sc_txt, (10,10))

            if score >= cfg['goal']: 
                state = STATE_VICTORY
                victory_timer = pygame.time.get_ticks() # Guardamos la hora exacta de la victoria

        elif state == STATE_GAMEOVER:
            for p in pipes: p.draw(screen)
            heart.draw(screen)
            draw_text_centered(screen, "GAME OVER", FONT_TITLE, (255,50,50), -50)
            draw_text_centered(screen, "Espacio para Menú", FONT_MAIN, (255,255,255), 50)

        elif state == STATE_VICTORY:
            screen.fill(COLOR_VICTORY_BG)
            # Decoración
            for _ in range(5):
                rx = random.randint(0, SCREEN_WIDTH)
                ry = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(screen, (255,100,100), (rx, ry), 5)

            # Texto actualizado
            msg = "I love you so much Coldy felices 1 año y 4 meses, no veas como pasan volando, porque siento que he estado una eternidad contigo porque disfruto mucho de tú compañia y amor ¡Te amo muchooo coldy culona!"
            
            draw_text_centered(screen, "¡FELIZ ANIVERSARIO! UuoUOuuuoOouu xd", FONT_TITLE, (255,255,255), -200)
            
            rect_txt = pygame.Rect(40, 150, 320, 400)
            wrap_text(screen, msg, FONT_MAIN, (139,0,0), rect_txt)
            
            # Lógica visual del botón salir
            current_time = pygame.time.get_ticks()
            if current_time - victory_timer > 3000:
                # Solo muestra el texto si ya se puede salir
                draw_text_centered(screen, "[Espacio para salir]", FONT_VICTORY, (255,255,255), 250)
            else:
                # Opcional: Mostrar cuánto falta o simplemente nada para que lea
                pass

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()