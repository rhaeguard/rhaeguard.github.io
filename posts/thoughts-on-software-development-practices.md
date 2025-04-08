<!--
title = Thoughts on Software Development Pratices
date = 2024-07-16T04:18:33-06:00
draft = false
-->

These are some of my random thoughts on software development pratices. These are not facts, these are opinions. I reckon you most likely have seen or heard some or all of these at some point.

 - Both [vertical scaling](https://en.wikipedia.org/wiki/Scalability#Vertical_or_scale_up) and [horizontal scaling](https://en.wikipedia.org/wiki/Scalability#Horizontal_or_scale_out) have their time and place. Not every architecture needs to be distributed microservices. A monolith is fine, most of the time.
 - Performance matters. As developers, it is professional to deliver a product that is performant. That is what we're being paid to do.
 - Measure the performance. Data-driven decisions should be preferred over intuition whenever possible.
 - Give visual feedback on any action the user performs in the UI. If the payment was successful, show the user that it was successful.
 - Do not generalize off of a single use case. You can literally fit an infinite number of lines through a single point.
 - Do not overengineer. If a `boolean` flag works fine in the current use case, use that. "Futureproofing" is a good concept but it often fails to deliver what it promises. Do not try to solve a problem that does not exist. Solve for your current problem.
 - Keep things simple. Simple does not mean trivial. It means doing only what you need to do. Casey Muratori has [an excellent lecture](https://youtu.be/Ge3aKEmZcqY) on this.
 - Code duplication is okay.
 - Old ideas get ressurrected every 10 years or so (SSR, SOAP/RPC/GraphQL in web development for examnple) therefore do not fixate on the new and shiny, but do keep up with the trends. Just because a random guy on the internet said jQuery or PHP is bad, doesn't mean it is bad. 
 - Learn how to use development tools properly. These include: IDEs, profilers, static analysis tools, perf testing tools, etc. and of course the AI assistants.
 - Test with real data. Mocking should/will never give you confidence to push things to production. Unit testing is important, but a unit does not mean a single function. Test the use cases: user login, purchase, refund, etc.
 - Be a generalist, learn the fundamentals. Nothing can replace a proper Computer Science knowledge a university undergrad study provides you.
 - Be open to ideas. Software Engineering is a fast moving field. It will have a lot of hyped up trends that you shouldn't spend time on as long as it isn't your job (and big corporations love hype trains), but it will also have really interesting and useful ideas. Keep an eye out for those. With experience you will learn what is fad and what's real deal.
 - Have a pre-recorded demo ready for your presentations; demo gods are often cruel. If you're presenting over Zoom, do not have transition animations.
 - Stop bikeshedding around variable naming, function naming, cases, language choices, formatting, etc. When working in a team, pick a style and stick to that, or if the team is already using one, use that.
 - Usually a series of `if`s or `switch` cases are better than inheritance. The problems people mention about conditionals is often overblown. Inheritance introduces way more bloat for simple use cases. It absolutely has its own time and place. "Composition over inheritance" is actually a good advice.
 - You do not need to introduce a whole new library/dependency to calculate something like the [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance).

