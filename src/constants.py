DEBUG = False

CSS_PATH = "./style.css"
XSLT_PATH = "./template.xsl"
XSLT_PATH_FROM_XML = "../template.xsl"

XSLT_CONTENT = """<?xml version="1.0"?>
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
"""

CSS_CONTENT = """body {
	margin: 2%;
	align-content: center;
}

@keyframes new_border_animation {
	0%   {border-color: hsl(0,   100%, 50%);}
	10%  {border-color: hsl(36,  100%, 50%);}
	20%  {border-color: hsl(72,  100%, 50%);}
	30%  {border-color: hsl(108, 100%, 50%);}
	40%  {border-color: hsl(144, 100%, 50%);}
	50%  {border-color: hsl(180, 100%, 50%);}
	60%  {border-color: hsl(216, 100%, 50%);}
	70%  {border-color: hsl(252, 100%, 50%);}
	80%  {border-color: hsl(288, 100%, 50%);}
	90%  {border-color: hsl(324, 100%, 50%);}
	100% {border-color: hsl(360, 100%, 50%);}
}

.item {
	position: relative;
	/* align-content: space-between; */
	border: 1px solid black;
	border-radius: 10px;
	float: left;
	width: 14.5%;
	height: 200px;
	margin: 0.5%;
	padding: 5px;
	overflow-y: visible;
}

.item.new {
	border-width: 2px;
	animation-name: new_border_animation;
	animation-duration: 5s;
	animation-direction: normal;
	animation-timing-function: linear;
	animation-iteration-count: infinite;
}

.pubDate {
	position: absolute;
	margin: auto;
	right: 10px;
	bottom: 10px;
	cursor: default;

	-webkit-user-select: none;  /* Chrome all / Safari all */
	-moz-user-select: none;     /* Firefox all */
	-ms-user-select: none;      /* IE 10+ */
	user-select: none;          /* Likely future */      
}
"""