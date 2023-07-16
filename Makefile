all:
	# python get_abstracts.py
	python process_abstracts.py
	python run_topic_modeling.py
clean:
	-rm data/cleaned_abstracts*
	-rm data/bigrammed_cleaned_abstracts*
	-rm data/lda_models/*

fit:
	python fit_dynamic_topic_model.py
fit2022:
	python fit_dynamic_topic_model.py --year 2022
