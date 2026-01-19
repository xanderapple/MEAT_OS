<%*
		title = await tp.system.prompt("Title"); 
		await tp.file.rename(`${title}`); 
%>

# <%* tR += `${title}` %>
Edited on [[<% tp.date.now("YYYY-MM-DD") %>]]

