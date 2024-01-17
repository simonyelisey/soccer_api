--sum of cleansheets by teams through seasons

INSERT INTO cleansheets_aggregations
with max_time as (
	select 
		c.season, 
		c.league,
		max(c.time_extraction) as max_time_extraction
	from cleansheets c
	where c.season in (%s)
	group by c.season, c.league
)
select 
	c.team, 
	c.league, 
	c.season,
	sum(c.games) as sum_games,
	now()::timestamp as time_extraction
from cleansheets c
inner join max_time
on max_time.season = c.season
and max_time.league = c.league
and max_time.max_time_extraction = c.time_extraction
group by c.season, c.league, c.team, c.time_extraction