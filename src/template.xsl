<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html"/>
	<xsl:template match="/rss">
		<html>
			<head>
				<meta http-equiv="Content-Type" 
					content="text/html; charset=utf-8"/>
				<link rel="stylesheet" href="../style.css"/>
				<title>RSS Feed Reader</title>
			</head>
			<body>
				<xsl:for-each select="channel/item">
					<div class="item">
						<xsl:if test="@new='new'">
							<xsl:attribute name="class">item new</xsl:attribute>
						</xsl:if>
						<h3 class="title">
							<a target="_blank"><xsl:attribute name="href"><xsl:value-of select="link" /></xsl:attribute>
								<xsl:value-of select="title" />
							</a>
						</h3>
						<h6 class="pubDate"><xsl:value-of select="pubDate" /></h6>
					</div>
				</xsl:for-each>
			</body>
		</html> 	
	</xsl:template>
</xsl:stylesheet>
