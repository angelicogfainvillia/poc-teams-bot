.PHONY: clean removeEmbs removeVectordbs removeArtifacts

SHELL=/bin/bash

## Delete all .png, .csv, .txt, .egg-info directories and cache files
clean:
	find . -name "__pycache__" -type d -exec rm -r {} \+
	find . -name "*.egg-info" -type d -exec rm -r {} \+

## Remove all files in the subdirectories of the embeddings directory
removeEmbs:
	find ./artifacts/embeddings/* -type f ! -name .gitkeep -exec rm {} +

## Remove all files inside any 'vectordb' directory within the 'artifacts' directory structure
removeVectordbs:
	for dir in $$(find ./artifacts -type d -name "vectordb"); do \
		find $$dir -type f ! -name .gitkeep -exec rm {} \; ; \
	done

## Apply both removeEmbs and removeVectordbs
removeArtifacts: removeEmbs removeVectordbs