"""
----- Shard(Searchable) -----
    Implements Searchable objects.

----- Shard Extractor -----
    get_shards()
    populate_shards()

----- Searchable -----
funcs:
    in_space()
    generate_trajectories() 'spherical' | 'cube' | 'random' | 'hyperplane'
    generate_start_point()
    generate_trajectories_from_start_point()
    add_trajectories()
    add_start_point()
    remove_trajectories()
    remove_start_point()
    search()
props:
    start_point
    trajectories

---- Analyzer(Module) ----
    Implements Module
    analise()       [preform searches in all shards of the CMF and analise the data from them]
    rank_shards()   [choose which shards are relevant to the constant for deeper search and rank higher if delta is not -1]

---- Module ----
    execute_module(*args, **kwargs)
"""