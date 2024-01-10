function setup_logging() {
    this.logger = logging.getLogger('BombeRLeWorld');
    this.logger.setLevel(s.LOG_GAME);
    var handler = new logging.FileHandler(`${this.args.log_dir}/game.log`, 'w');
    handler.setLevel(logging.DEBUG);
    var formatter = new logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s');
    handler.setFormatter(formatter);
    this.logger.addHandler(handler);
    this.logger.info('Initializing game world');
}