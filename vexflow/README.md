# VexFlow MusicXML plugin

A plugin for parsing and engraving MusicXML documents
in [VexFlow](https://github.com/0xFE/vexflow).
Thanks to @wilson428 for reorganizing the project as a plugin,
so it can be worked on independently of the upstream VexFlow.

## Installation

Clone this repo and install the dependencies

	git clone git@github.com:mechanicalscribe/vexflow-musicxml.git && cd vexflow-musicxml
	npm install

	./build.js --include-vexflow

This will generate a file called [vexflow.musicxml.js](vexflow.musicxml.js). To use it, all you need to do is include it.

	<script src="vexflow.musicxml.js"></script>

After building the script you can see this in action at [demo/index.html](demo/index.html), though you'll need to spin up a server since the page makes an AJAX call to the XML file with the actual music in it:

	python -m SimpleHTTPServer 8080

Then head on over to [localhost:8080/demo/index.html](http://localhost:8080/demo/index.html) for some Moonlight Sonata rendered live in your browser.

## Build options

To skip the VexFlow source and just use this as a plugin, omit `--include-vexflow` in the build:

	./build.js

Then you'd want to do something like:

	<script src="node_modules/vexflow/releases/vexflow-min.js"></script>
	<script src="vexflow.musicxml.js"></script>

To include source maps:

	./build.js --debug

To include Vexflow from somewhere other than `node_modules`:

	./build.js --path=path/to/vexflow/js_file
