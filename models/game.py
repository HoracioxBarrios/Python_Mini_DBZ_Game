# MIT License
#
# Copyright (c) 2023 [UTN FRA](https://fra.utn.edu.ar/) All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import pygame as pg
from models.constants import (
    ALTO_VENTANA, ANCHO_VENTANA, FPS, DEBUG
)
from models.playable.player.main_player import Player
from models.stage import Stage
from models.video_player.pyvidplayer import Video

class Game:

    def __init__(self) -> None:
        self.__executing = True
        self.__screen_surface = pg.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pg.init()
        self.__actual_stage_number = 1
        self.__clock = pg.time.Clock()
        self.__actual_stage: Stage = None
        self.__video_length_time = None
        self.__video_initial_time = 0
        self.__initial_player_config = self.__get_configs().get('player')
        self.__transform_transition_vid_path = './assets/video/player_ssj2_transition.mp4'
        self.__end_transition_vid_path = './assets/video/player_ssj2_end_battle.mp4'
        self.__is_playing_last_video = False
    
    def __get_configs(self) -> dict:
        with open('./configs/config.json', 'r') as configs:
            return json.load(configs)[f'stage_{self.__actual_stage_number}']

    def __play_video_transition(self, path: str, ancho: int, alto: int, delta_ms)-> None:
        vid_1 = Video(path)
        vid_1.set_size((ancho, alto))
        vid_1.set_volume(0.3)
        self.__video_initial_time = int(pg.time.get_ticks() / 1000)
        if not self.__video_length_time:
            self.__video_length_time = vid_1.duration
            if DEBUG:
                print(f'Duracion del video: {self.__video_length_time} segundos')
                print(f'El video inicio en: {self.__video_initial_time} segundos de haber comenzado el juego')

        running = True
        while running:
            if vid_1.active:
                
                vid_1.set_volume(0.9)
                vid_1.draw(self.__screen_surface, (0, 0))
            else:
                running = False
                vid_1.close()
            current_time = int(pg.time.get_ticks() / 1000)
            if current_time - self.__video_initial_time >= self.__video_length_time:
                running = False
                vid_1.close()
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    vid_1.close()
                    running = False
            pg.display.update()
        pg.display.update()

    def __set_game_title(self) -> None:
        if self.__actual_stage:
            match self.__actual_stage.stage_name:
                case 'stage_1':
                    pg.display.set_caption('Saga de Andriodes')
                case 'stage_2':
                    pg.display.set_caption('Inicio Saga de Cell')
                case 'stage_3':
                    pg.display.set_caption('Batalla Contra Cell')
                case 'stage_4':
                    pg.display.set_caption('Batalla Final Contra Cell')

    def run_game(self):
        player_gohan = Player(self.__screen_surface, 50, 350, frame_rate=70, speed_walk=20, speed_run=40)
        player_gohan.initial_config(self.__initial_player_config.get('hp'), self.__initial_player_config.get('mp'))

        while self.__executing:
            delta_ms = self.__clock.tick(FPS)
            # si no instancie ningun stage AUN o ya gane el stage, instancio el siguiente
            if not self.__actual_stage or self.__actual_stage.stage_passed():
                if self.__actual_stage_number < 5:
                    
                    if self.__actual_stage and self.__actual_stage.stage_passed() and self.__actual_stage.stage_name == 'stage_3':
                        self.__play_video_transition(self.__transform_transition_vid_path,  ANCHO_VENTANA, ALTO_VENTANA, delta_ms)
                        self.__actual_stage.player_sprite.do_transformation()
                    self.__actual_stage = Stage(self.__screen_surface, player_gohan, ANCHO_VENTANA, ALTO_VENTANA, f'stage_{self.__actual_stage_number}')
                    self.__set_game_title()
                    print(self.__actual_stage.stage_name)
                    self.__actual_stage_number += 1 # incremento en 1 el stage para cuando tenga que volver a instanciar el nuevo
                    
                if self.__actual_stage and self.__actual_stage.stage_passed() and\
                    self.__actual_stage.stage_name == 'stage_4' and not self.__is_playing_last_video:
                    self.__is_playing_last_video = True
                    self.__play_video_transition(self.__end_transition_vid_path,  ANCHO_VENTANA, ALTO_VENTANA, delta_ms)

            #print(delta_ms)
            events_list = pg.event.get()
            for event in events_list:
                match event.type:
                    case pg.QUIT:
                        print('Estoy CERRANDO el JUEGO')
                        self.__executing = False
                        break
                    case pg.MOUSEBUTTONDOWN:
                        message = f'Click coords: {event.pos}'
                        print(message)
            
            key_pressed_list = pg.key.get_pressed()
            self.__screen_surface.blit(self.__actual_stage.bkg_img, self.__actual_stage.bkg_img.get_rect())
            self.__actual_stage.run(delta_ms, key_pressed_list, events_list)
            pg.display.update()

        pg.quit()