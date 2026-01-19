<%*
	let title = tp.file.title 
	if (title.startsWith("Untitled")) { 
		title = await tp.system.prompt("Title"); 
		await tp.file.rename(`${title}`); 
		} 
	tR += "---"
%>
Tags: 
Aliases: []
Created: <% tp.file.creation_date("YYYY-MM-DD") %>
---

# <%* tR += `${title}` %>
Created on [[<% tp.file.creation_date("YYYY-MM-DD") %>]]

<% tp.file.cursor() %>

---
## References

