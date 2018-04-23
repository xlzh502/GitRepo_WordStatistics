import html.parser
import pdb
import re

class DocParser(html.parser.HTMLParser):
	def __init__(self):
		html.parser.HTMLParser.__init__(self)
		self.seen=set()
		self.result=""
	
	def handle_starttag(self, tag, attributes):
		if (tag.lower() == 'br'):
			self.result+='\n'
	
	def handle_data(self, data):
		self.result += data
			
	def handle_endtag(self, tag):
		if (tag.lower() == 'br'):
			self.result+='\n'
		
#strparse='<span style="color: #ff0000"><b>I.</b></span> <span style="color: #0000ff">verb active</span><BR>  Court, solicit in love, make love to, pay one\'s addresses to.<BR><span style="color: #ff0000"><b>II.</b></span> <span style="color: #0000ff">verb neuter</span><BR>  Court, make love.'
strparse='<div class="sdct_x"> <span class="xdxf_k">want</span> <br/> <span class="xdxf_abbr">  <i>   <span style="color:blue">v.</span>  </i> </span> <br/> <span class="xdxf_dtrn">  <b>1</b> desire, crave, wish (for), long for, pine for, hope (for), fancy, covet, hanker after, lust after, hunger for or after, thirst for or after, yearn for, <span class="xdxf_abbr">   <i>    <span style="color:blue">Colloq</span>   </i>  </span> have a yen for:</span> <br/>&nbsp;&nbsp; <i>  <span class="xdxf_ex_old">I want you near me. Ignore his crying - he just wants some ice-cream. Maybe he\'s crying because he wants to go.</span> </i> <br/> <span class="xdxf_dtrn">  <b>2</b> need, lack, miss, require, call for, demand, be deficient in, be or stand in want or in need of, necessitate; be or fall short of:</span> <br/>&nbsp;&nbsp; <i>  <span class="xdxf_ex_old">This engine wants proper maintenance. The bottle wants only a few more drops to fill it.</span> </i> <br/> <span class="xdxf_dtrn">n.</span> <br/> <span class="xdxf_dtrn">  <b>3</b> need, lack, shortage, deficiency, dearth, scarcity, scarceness, insufficiency, scantiness, inadequacy, paucity:</span> <br/>&nbsp;&nbsp; <i>  <span class="xdxf_ex_old">For want of good writers, the literary quarterly diminished in size and finally disappeared.</span> </i> <br/> <span class="xdxf_dtrn">  <b>4</b> appetite, hunger, thirst, craving, desire, fancy, wish, longing, yearning, hankering, demand, necessity, requirement, requisite, prerequisite, <span class="xdxf_abbr">   <i>    <span style="color:blue">Colloq</span>   </i>  </span> yen:</span> <br/>&nbsp;&nbsp; <i>  <span class="xdxf_ex_old">She gave up trying to satisfy his wants.</span> </i> <br/> <span class="xdxf_dtrn">  <b>5</b> poverty, need, indigence, homelessness, destitution, privation, pauperism, penury, neediness, impecuniousness:</span> <br/>&nbsp;&nbsp; <i>  <span class="xdxf_ex_old">The civilized nations are trying to solve the problems of want, which seem to increase daily.</span> </i></div>'

strparse=re.sub(r'>\s+<', r'><', strparse)

#pdb.set_trace() 
p = DocParser()
p.feed(strparse)

print(p.result)
