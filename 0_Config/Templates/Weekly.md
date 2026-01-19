---
tags: []
Aliases:
Created: <% tp.file.creation_date("YYYY-MM-DD") %>
---
# <% tp.file.title%>
Created at [[  <% tp.file.creation_date("MMMM Do, YYYY") %>  ]] <% tp.file.creation_date("HH:mm") %>

#### What's the Plan?



---

#### What's extraordinary?



---

#### What's on your mind?



---
#### Gemini Interactions

```dataview
LIST
FROM "1 Fleeting Notes/Capture/Gemini_Interactions.md"
WHERE dateformat(file.ctime, "yyyy-WW") = this.file.name
```

---
#### Weekly Logs
<!-- Dataview queries for weekly logs (Music Listening, Somatic Experiences, Technical Troubleshooting) need to be re-evaluated and implemented based on tags in the flattened structure. -->

---
#### This Week

```dataview
table without id file.link as "This Week",
dateformat(file.mday, "cccc") as On
WHERE date(<% tp.file.creation_date("YYYY-MM-DD") %>) - file.mday <= dur(7 days)
and file.mday >= date(<% tp.file.creation_date("YYYY-MM-DD") %>)
sort date(<% tp.file.creation_date("YYYY-MM-DD") %>) - file.mtime
```




## References


