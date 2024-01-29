function setup_logging(){
    this.logger = logging.getLogger('BombeRLeWorld');
    this.logger.setLevel(s.LOG_GAME);
    var handler = new logging.FileHandler(`${this.args.log_dir}/game.log`, 'w');
    handler.setLevel(logging.DEBUG);
    var formatter = new logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s');
    handler.setFormatter(formatter);
    this.logger.addHandler(handler);
    this.logger.info('Initializing game world');
}

function new_round() {
    if (this.running) {
        this.logger.warning('New round requested while still running');
        this.end_round();
    }
    var new_round = (this.round + 1);
    this.logger.info('STARTING ROUND #' + new_round);
    this.step = 0;
    this.bombs = [];
    this.explosions = [];
    if (this.args.match_name !== null) {
        var match_prefix = this.args.match_name + ' | ';
    } else {
        var match_prefix = '';
    }
    this.round_id = match_prefix + 'Round ' + ('' + new_round).padStart(2, '0') + ' (' + new Date().toLocaleString() + ')';
    [this.arena, this.coins, this.active_agents] = this.build_arena();
    for (var agent in this.active_agents) {
        agent.start_round();
    }
    this.replay = {'round': new_round, 'arena': np.array(this.arena), 'coins': this.coins.map(c => c.get_state()), 'agents': this.active_agents.map(a => a.get_state()), 'actions': {}, 'permutations': []};
    this.round = new_round;
    this.running = true;
}

function build_arena() {
    throw new Error('NotImplementedError');
}

function add_agent(agent_dir, name, train=false) {
    assert(this.agents.length < s.MAX_AGENTS);
    let backend = new SequentialAgentBackend(train, name, agent_dir);
    backend.start();
    let color = this.colors.pop();
    let agent = new Agent(name, agent_dir, name, train, backend, color, color);
    this.agents.push(agent);
}

function tile_is_free(self, x, y) {
    let is_free = (self.arena[(x, y)] == 0);
    if (is_free) {
        for (let obstacle of (self.bombs + self.active_agents)) {
            is_free = (is_free && ((obstacle.x != x) || (obstacle.y != y)));
        }
    }
    return is_free;
}

function perform_agent_action(agent, action) {
    if (action === 'UP' && this.tile_is_free(agent.x, agent.y - 1)) {
        agent.y -= 1;
        agent.add_event('MOVED_UP');
    } else if (action === 'DOWN' && this.tile_is_free(agent.x, agent.y + 1)) {
        agent.y += 1;
        agent.add_event('MOVED_DOWN');
    } else if (action === 'LEFT' && this.tile_is_free(agent.x - 1, agent.y)) {
        agent.x -= 1;
        agent.add_event('MOVED_LEFT');
    } else if (action === 'RIGHT' && this.tile_is_free(agent.x + 1, agent.y)) {
        agent.x += 1;
        agent.add_event('MOVED_RIGHT');
    } else if (action === 'BOMB' && agent.bombs_left) {
        console.info('Agent <' + agent.name + '> drops bomb at (' + agent.x + ', ' + agent.y + ')');
        this.bombs.push(new Bomb([agent.x, agent.y], agent, BOMB_TIMER, BOMB_POWER, agent.bomb_sprite));
        agent.bombs_left = false;
        agent.add_event('BOMB_DROPPED');
    } else if (action === 'WAIT') {
        agent.add_event('WAITED');
    } else {
        agent.add_event('INVALID_ACTION');
    }
}

function poll_and_run_agents() {
    throw new Error('NotImplementedError');
}

function send_game_events() {
    // code implementation goes here
    // pass
}

function do_step(self, user_input='WAIT') {
    assert(this.running);
    this.step += 1;
    this.logger.info(`STARTING STEP ${this.step}`);
    this.user_input = user_input;
    this.logger.debug(`User input: ${this.user_input}`);
    this.poll_and_run_agents();
    this.collect_coins();
    this.update_explosions();
    this.update_bombs();
    this.evaluate_explosions();
    this.send_game_events();
    if (this.time_to_stop()) {
        this.end_round();
    }
}

function collect_coins() {
    for (let coin of this.coins) {
        if (coin.collectable) {
            for (let a of this.active_agents) {
                if (a.x === coin.x && a.y === coin.y) {
                    coin.collectable = false;
                    this.logger.info(`Agent <${a.name}> picked up coin at (${a.x}, ${a.y}) and receives 1 point`);
                    a.update_score(s.REWARD_COIN);
                    a.add_event(e.COIN_COLLECTED);
                    a.trophies.push(Trophy.coin_trophy);
                }
            }
        }
    }
}

function update_explosions() {
    var remaining_explosions = [];
    for (var i = 0; i < this.explosions.length; i++) {
        var explosion = this.explosions[i];
        explosion.timer -= 1;
        if (explosion.timer <= 0) {
            explosion.next_stage();
            if (explosion.stage === 1) {
                explosion.owner.bombs_left = true;
            }
        }
        if (explosion.stage !== null) {
            remaining_explosions.push(explosion);
        }
    }
    this.explosions = remaining_explosions;
}

function update_bombs() {
    for (let bomb of this.bombs) {
        if (bomb.timer <= 0) {
            console.log(`Agent <${bomb.owner.name}>'s bomb at (${bomb.x}, ${bomb.y}) explodes`);
            bomb.owner.add_event(e.BOMB_EXPLODED);
            let blast_coords = bomb.get_blast_coords(this.arena);
            for (let [x, y] of blast_coords) {
                if (this.arena[(x, y)] === 1) {
                    this.arena[(x, y)] = 0;
                    bomb.owner.add_event(e.CRATE_DESTROYED);
                    for (let c of this.coins) {
                        if (c.x === x && c.y === y) {
                            c.collectable = true;
                            console.log(`Coin found at (${x}, ${y})`);
                            bomb.owner.add_event(e.COIN_FOUND);
                        }
                    }
                }
            }
            let screen_coords = blast_coords.map(([x, y]) => (s.GRID_OFFSET[0] + (s.GRID_SIZE * x), s.GRID_OFFSET[1] + (s.GRID_SIZE * y)));
            this.explosions.push(new Explosion(blast_coords, screen_coords, bomb.owner, s.EXPLOSION_TIMER));
            bomb.active = false;
        } else {
            bomb.timer -= 1;
        }
    }
    this.bombs = this.bombs.filter(b => b.active);
}

function evaluate_explosions() {
  const agents_hit = new Set();
  for (const explosion of this.explosions) {
    if (explosion.is_dangerous()) {
      for (const a of this.active_agents) {
        if (!a.dead && explosion.blast_coords.has(`${a.x},${a.y}`)) {
          agents_hit.add(a);
          if (a === explosion.owner) {
            this.logger.info(`Agent <${a.name}> blown up by own bomb`);
            a.add_event(e.KILLED_SELF);
            explosion.owner.trophies.push(Trophy.suicide_trophy);
          } else {
            this.logger.info(`Agent <${a.name}> blown up by agent <${explosion.owner.name}>'s bomb`);
            this.logger.info(`Agent <${explosion.owner.name}> receives 1 point`);
            explosion.owner.update_score(s.REWARD_KILL);
            explosion.owner.add_event(e.KILLED_OPPONENT);
            explosion.owner.trophies.push(pygame.transform.smoothscale(a.avatar, [15, 15]));
          }
        }
      }
    }
  }
  for (const a of agents_hit) {
    a.dead = true;
    this.active_agents.splice(this.active_agents.indexOf(a), 1);
    a.add_event(e.GOT_KILLED);
    for (const aa of this.active_agents) {
      if (aa !== a) {
        aa.add_event(e.OPPONENT_ELIMINATED);
      }
    }
  }
}

function end_round() {
    if (!this.running) {
        throw new Error('End-of-round requested while no round was running');
    }
    this.running = false;
    for (var i = 0; i < this.agents.length; i++) {
        var a = this.agents[i];
        a.note_stat('score', a.score);
        a.note_stat('rounds');
    }
    this.round_statistics[this.round_id] = {
        'steps': this.step,
        ...Object.keys(this.agents[0].statistics).reduce((acc, key) => {
            acc[key] = this.agents.reduce((sum, a) => sum + a.statistics[key], 0);
            return acc;
        }, {})
    };
}

function time_to_stop() {
    if (this.active_agents.length === 0) {
        this.logger.info('No agent left alive, wrap up round');
        return true;
    }
    if (
        this.active_agents.length === 1 &&
        this.arena.every(row => row.every(cell => cell === 0)) &&
        this.coins.every(coin => !coin.collectable) &&
        (this.bombs.length + this.explosions.length === 0)
    ) {
        this.logger.info('One agent left alive with nothing to do, wrap up round');
        return true;
    }
    if (
        this.agents.some(a => a.train) &&
        !this.args.continue_without_training &&
        !this.active_agents.some(a => a.train)
    ) {
        this.logger.info('No training agent left alive, wrap up round');
        return true;
    }
    if (this.step >= s.MAX_STEPS) {
        this.logger.info('Maximum number of steps reached, wrap up round');
        return true;
    }
    return false;
}

function end() {
    if (this.running) {
        this.end_round();
    }
    let results = { 'by_agent': {} };
    for (let a of this.agents) {
        results['by_agent'][a.name] = a.lifetime_statistics;
        results['by_agent'][a.name]['score'] = a.total_score;
    }
    results['by_round'] = this.round_statistics;
    if (this.args.save_stats !== false) {
        let file_name;
        if (this.args.save_stats !== true) {
            file_name = this.args.save_stats;
        } else if (this.args.match_name !== null) {
            file_name = `results/${this.args.match_name}.json`;
        } else {
            file_name = `results/${new Date().toISOString().slice(0, 19).replace('T', ' ')}.json`;
        }
        let name = new Path(file_name);
        if (!name.parent.exists()) {
            name.parent.mkdir({ recursive: true });
        }
        let file = name.open('w');
        file.write(JSON.stringify(results, null, 4));
        file.close();
    }
}

function setup_agents(agents) {
  this.agents = [];
  for (let [agent_dir, train] of agents) {
    if (agents.filter(([d, t]) => d === agent_dir).length > 1) {
      let count = this.agents.filter(a => a.code_name === agent_dir).length;
      let name = agent_dir + '_' + count;
    } else {
      let name = agent_dir;
    }
    this.add_agent(agent_dir, name, { train: train });
  }
}

function build_arena() {
    const WALL = -1;
    const FREE = 0;
    const CRATE = 1;
    const arena = Array(s.COLS).fill(Array(s.ROWS).fill(0));
    const scenario_info = s.SCENARIOS[this.args.scenario];
    for (let i = 0; i < s.COLS; i++) {
        for (let j = 0; j < s.ROWS; j++) {
            arena[i][j] = Math.random() < scenario_info['CRATE_DENSITY'] ? CRATE : FREE;
        }
    }
    for (let i = 0; i < s.COLS; i++) {
        arena[i][0] = WALL;
        arena[i][s.ROWS - 1] = WALL;
    }
    for (let j = 0; j < s.ROWS; j++) {
        arena[0][j] = WALL;
        arena[s.COLS - 1][j] = WALL;
    }
    for (let x = 0; x < s.COLS; x++) {
        for (let y = 0; y < s.ROWS; y++) {
            if ((((x + 1) * (y + 1)) % 2) === 1) {
                arena[x][y] = WALL;
            }
        }
    }
    const start_positions = [[1, 1], [1, s.ROWS - 2], [s.COLS - 2, 1], [s.COLS - 2, s.ROWS - 2]];
    for (let i = 0; i < start_positions.length; i++) {
        const [x, y] = start_positions[i];
        const positions = [[x, y], [x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]];
        for (let j = 0; j < positions.length; j++) {
            const [xx, yy] = positions[j];
            if (arena[xx][yy] === CRATE) {
                arena[xx][yy] = FREE;
            }
        }
    }
    const coins = [];
    const all_positions = [];
    for (let i = 0; i < s.COLS; i++) {
        for (let j = 0; j < s.ROWS; j++) {
            all_positions.push([i, j]);
        }
    }
    const crate_positions = all_positions.filter(([x, y]) => arena[x][y] === CRATE);
    const free_positions = all_positions.filter(([x, y]) => arena[x][y] === FREE);
    const coin_positions = crate_positions.concat(free_positions).slice(0, scenario_info['COIN_COUNT']);
    for (let i = 0; i < coin_positions.length; i++) {
        const [x, y] = coin_positions[i];
        coins.push(new Coin([x, y], arena[x][y] === FREE));
    }
    const active_agents = [];
    const start_positions_permuted = start_positions.sort(() => Math.random() - 0.5);
    for (let i = 0; i < this.agents.length; i++) {
        active_agents.push(this.agents[i]);
        this.agents[i].x = start_positions_permuted[i][0];
        this.agents[i].y = start_positions_permuted[i][1];
    }
    return [arena, coins, active_agents];
}

function get_state_for_agent(agent) {
    if (agent.dead) {
        return null;
    }
    var state = {
        'round': this.round,
        'step': this.step,
        'field': this.arena.slice(),
        'self': agent.get_state(),
        'others': this.active_agents.filter(function(other) {
            return other !== agent;
        }).map(function(other) {
            return other.get_state();
        }),
        'bombs': this.bombs.map(function(bomb) {
            return bomb.get_state();
        }),
        'coins': this.coins.filter(function(coin) {
            return coin.collectable;
        }).map(function(coin) {
            return coin.get_state();
        }),
        'user_input': this.user_input
    };
    var explosion_map = Array(this.arena.length).fill(null).map(function() {
        return Array(this.arena[0].length).fill(0);
    });
    this.explosions.forEach(function(exp) {
        if (exp.is_dangerous()) {
            exp.blast_coords.forEach(function(coord) {
                explosion_map[coord[0]][coord[1]] = Math.max(explosion_map[coord[0]][coord[1]], exp.timer - 1);
            });
        }
    });
    state['explosion_map'] = explosion_map;
    return state;
}

function poll_and_run_agents() {
    for (let a of this.active_agents) {
        let state = this.get_state_for_agent(a);
        a.store_game_state(state);
        a.reset_game_events();
        if (a.available_think_time > 0) {
            a.act(state);
        }
    }
    let perm = this.rng.permutation(this.active_agents.length);
    this.replay['permutations'].push(perm);
    for (let i of perm) {
        let a = this.active_agents[i];
        if (a.available_think_time > 0) {
            try {
                let [action, think_time] = a.wait_for_act();
            } catch (error) {
                if (!(error instanceof KeyboardInterrupt)) {
                    if (!this.args.silence_errors) {
                        throw error;
                    }
                }
                action = 'ERROR';
                think_time = Infinity;
            }
            this.logger.info(`Agent <${a.name}> chose action ${action} in ${think_time.toFixed(2)}s.`);
            if (think_time > a.available_think_time) {
                let next_think_time = a.base_timeout - (think_time - a.available_think_time);
                this.logger.warning(`Agent <${a.name}> exceeded think time by ${(think_time - a.available_think_time).toFixed(2)}s. Setting action to "WAIT" and decreasing available time for next round to ${next_think_time.toFixed(2)}s.`);
                action = 'WAIT';
                a.trophies.push(Trophy.time_trophy);
                a.available_think_time = next_think_time;
            } else {
                this.logger.info(`Agent <${a.name}> stayed within acceptable think time.`);
                a.available_think_time = a.base_timeout;
            }
        } else {
            this.logger.info(`Skipping agent <${a.name}> because of last slow think time.`);
            a.available_think_time += a.base_timeout;
            action = 'WAIT';
        }
        this.replay['actions'][a.name].push(action);
        this.perform_agent_action(a, action);
    }
}

function send_game_events() {
    for (var i = 0; i < this.agents.length; i++) {
        var a = this.agents[i];
        if (a.train) {
            if (!a.dead) {
                a.process_game_events(this.get_state_for_agent(a));
            }
            for (var j = 0; j < this.active_agents.length; j++) {
                var enemy = this.active_agents[j];
                if (enemy !== a) {
                    // code here
                }
            }
        }
    }
    for (var i = 0; i < this.agents.length; i++) {
        var a = this.agents[i];
        if (a.train) {
            if (!a.dead) {
                a.wait_for_game_event_processing();
            }
            for (var j = 0; j < this.active_agents.length; j++) {
                var enemy = this.active_agents[j];
                if (enemy !== a) {
                    // code here
                }
            }
        }
    }
}

function end_round() {
    if (this.agents.length == 2) {
        if (!fs.existsSync('elo')) {
            fs.mkdirSync('elo');
        }
        fs.appendFileSync('elo/elo.log', `${this.agents[0].code_name} ${(this.agents[0].score == this.agents[1].score) ? '=' : (this.agents[0].score < this.agents[1].score) ? '<' : '>'} ${this.agents[1].code_name}\n`);
    }
    this.logger.info(`WRAPPING UP ROUND #${this.round}`);
    for (let a of this.active_agents) {
        a.add_event(e.SURVIVED_ROUND);
    }
    for (let a of this.agents) {
        if (a.train) {
            a.round_ended();
        }
    }
    if (this.args.save_replay) {
        this.replay['n_steps'] = this.step;
        let name = ((this.args.save_replay === true) ? `replays/${this.round_id}.pt` : this.args.save_replay);
        fs.writeFileSync(name, JSON.stringify(this.replay));
    }
}

function end() {
    Object.getPrototypeOf(this).end.call(this);
    this.logger.info('SHUT DOWN');
    for (let a of this.agents) {
        this.logger.debug(`Sending exit message to agent <${a.name}>`);
    }
}

function render_text(self, text, x, y, color, halign='left', valign='top', size='medium', aa=false) {
    var text_surface = self.fonts[size].render(text, aa, color);
    var text_rect = text_surface.get_rect();
    if (halign === 'left') {
        text_rect.left = x;
    }
    if (halign === 'center') {
        text_rect.centerx = x;
    }
    if (halign === 'right') {
        text_rect.right = x;
    }
    if (valign === 'top') {
        text_rect.top = y;
    }
    if (valign === 'center') {
        text_rect.centery = y;
    }
    if (valign === 'bottom') {
        text_rect.bottom = y;
    }
    self.screen.blit(text_surface, text_rect);
}

function render() {
    this.screen.blit(this.background, [0, 0]);
    if (this.world.round === 0) {
        return;
    }
    this.frame += 1;
    pygame.display.set_caption(`BombeRLe | Round #${this.world.round}`);
    for (let x = 0; x < this.world.arena.shape[1]; x++) {
        for (let y = 0; y < this.world.arena.shape[0]; y++) {
            if (this.world.arena.get([x, y]) === -1) {
                this.screen.blit(this.t_wall, [s.GRID_OFFSET[0] + (s.GRID_SIZE * x), s.GRID_OFFSET[1] + (s.GRID_SIZE * y)]);
            }
            if (this.world.arena.get([x, y]) === 1) {
                this.screen.blit(this.t_crate, [s.GRID_OFFSET[0] + (s.GRID_SIZE * x), s.GRID_OFFSET[1] + (s.GRID_SIZE * y)]);
            }
        }
    }
    this.render_text(`Step ${this.world.step}`, s.GRID_OFFSET[0], s.HEIGHT - (s.GRID_OFFSET[1] / 2), [64, 64, 64], {valign: 'center', halign: 'left', size: 'medium'});
    for (const bomb of this.world.bombs) {
        bomb.render(this.screen, s.GRID_OFFSET[0] + (s.GRID_SIZE * bomb.x), s.GRID_OFFSET[1] + (s.GRID_SIZE * bomb.y));
    }
    for (const coin of this.world.coins) {
        if (coin.collectable) {
            coin.render(this.screen, s.GRID_OFFSET[0] + (s.GRID_SIZE * coin.x), s.GRID_OFFSET[1] + (s.GRID_SIZE * coin.y));
        }
    }
    for (const agent of this.world.active_agents) {
        agent.render(this.screen, s.GRID_OFFSET[0] + (s.GRID_SIZE * agent.x), s.GRID_OFFSET[1] + (s.GRID_SIZE * agent.y));
    }
    for (const explosion of this.world.explosions) {
        explosion.render(this.screen);
    }
    const agents = this.world.agents;
    const leading = agents.reduce((a, b) => a.score > b.score ? a : b);
    const y_base = s.GRID_OFFSET[1] + 15;
    for (let i = 0; i < agents.length; i++) {
        const bounce = (agents[i] !== leading || this.world.running) ? 0 : Math.abs(10 * Math.sin(5 * time()));
        agents[i].render(this.screen, 600, (y_base + (50 * i) - 15) - bounce);
        this.render_text(agents[i].display_name, 650, y_base + (50 * i), agents[i].dead ? [64, 64, 64] : [255, 255, 255], {valign: 'center', size: 'small'});
        for (let j = 0; j < agents[i].trophies.length; j++) {
            this.screen.blit(agents[i].trophies[j], [660 + (10 * j), (y_base + (50 * i)) + 12]);
        }
        this.render_text(`${agents[i].score}`, 830, y_base + (50 * i), [255, 255, 255], {valign: 'center', halign: 'right', size: 'big'});
        this.render_text(`${agents[i].total_score}`, 890, y_base + (50 * i), [64, 64, 64], {valign: 'center', halign: 'right', size: 'big'});
    }
    if (!this.world.running) {
        const x_center = ((((s.WIDTH - s.GRID_OFFSET[0]) - (s.COLS * s.GRID_SIZE)) / 2) + s.GRID_OFFSET[0]) + (s.COLS * s.GRID_SIZE);
        const color = [
            255 * ((Math.sin(3 * time()) / 3) + 0.66),
            255 * ((Math.sin((4 * time()) + (Math.PI / 3)) / 3) + 0.66),
            255 * ((Math.sin((5 * time()) - (Math.PI / 3)) / 3) + 0.66)
        ];
        this.render_text(leading.display_name, x_center, 320, color, {valign: 'top', halign: 'center', size: 'huge'});
        this.render_text('has won the round!', x_center, 350, color, {valign: 'top', halign: 'center', size: 'big'});
        const leading_total = agents.reduce((a, b) => a.total_score > b.total_score ? a : b);
        if (leading_total === leading) {
            this.render_text(`${leading_total.display_name} is also in the lead.`, x_center, 390, [128, 128, 128], {valign: 'top', halign: 'center', size: 'medium'});
        } else {
            this.render_text(`But ${leading_total.display_name} is in the lead.`, x_center, 390, [128, 128, 128], {valign: 'top', halign: 'center', size: 'medium'});
        }
    }
    if (this.world.running && this.world.args.make_video) {
        this.world.logger.debug(`Saving screenshot for frame ${this.frame}`);
        pygame.image.save(this.screen, String(this.screenshot_dir / `${this.world.round_id}_${this.frame.toString().padStart(5, '0')}.png`));
    }
}

function make_video() {
    assert (this.world.args.make_video !== false);
    if (this.world.args.make_video === true) {
        var files = [
            this.screenshot_dir + '/' + this.world.round_id + '_video.mp4',
            this.screenshot_dir + '/' + this.world.round_id + '_video.webm'
        ];
    } else {
        var files = [Path(this.world.args.make_video)];
    }
    this.world.logger.debug('Turning screenshots into video');
    var PARAMS = {
        '.mp4': ['-preset', 'veryslow', '-tune', 'animation', '-crf', '5', '-c:v', 'libx264', '-pix_fmt', 'yuv420p'],
        '.webm': ['-threads', '2', '-tile-columns', '2', '-frame-parallel', '0', '-g', '100', '-speed', '1', '-pix_fmt', 'yuv420p', '-qmin', '0', '-qmax', '10', '-crf', '5', '-b:v', '2M', '-c:v', 'libvpx-vp9']
    };
    for (var i = 0; i < files.length; i++) {
        var video_file = files[i];
        subprocess.call(['ffmpeg', '-y', '-framerate', '' + this.world.args.fps, '-f', 'image2', '-pattern_type', 'glob', '-i', this.screenshot_dir + '/' + this.world.round_id + '_*.png'].concat(PARAMS[video_file.split('.').pop()], video_file));
    }
    this.world.logger.info('Done writing videos.');
    for (var _i = 0, _a = this.screenshot_dir.glob(this.world.round_id + '_*.png'); _i < _a.length; _i++) {
        var f = _a[_i];
        f.unlink();
    }
}

