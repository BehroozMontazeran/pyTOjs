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