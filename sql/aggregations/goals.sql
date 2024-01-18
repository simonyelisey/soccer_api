--sum of goals (for/against) by teams through seasons

INSERT INTO goals_aggregations
with max_time as (
	select 
		g.season, 
		g.league,
		max(g.time_extraction) as max_time_extraction
	from goals g
	where g.season in (%s)
	group by g.season, g.league
)
select 
	g.team, 
	g.league, 
	g.season,
	g.direction,
	sum(g.goals) as sum_goals,
	now()::timestamp as time_extraction
from goals g
inner join max_time
on max_time.season = g.season
and max_time.league = g.league
and max_time.max_time_extraction = g.time_extraction
group by g.season, g.league, g.team, g.direction, g.time_extraction