from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

##############################################################################
# UVODNA STRAN
##############################################################################
@main_bp.route('/')
def index():
    long_text = """Cilj seminarske naloge je razviti spletno aplikacijo, ki uporabnikom omogoča sprejemanje informiranih 
    odločitev pri investicijah z uporabo metodologij za večkriterijsko odločanje (MCDA)."""
    
    company_choice = """Prvih 20 podjetij na seznamu Fortune 500 predstavlja globalno najbolj vplivna podjetja, ki so vodilna
    v svojih panogah. Njihov vpliv na svetovno gospodarstvo je velik, kar omogoča izvedbo analize na podlagi pomembnih in aktualnih podatkov."""
    
    criteria_choice = """Za analizo podjetij sem uporabil naslednje kriterije, pridobljene iz podatkov Fortune 500. Prihodek ($): Meri skupni 
    prihodek podjetja v določenem obdobju. Pomeni finančno stabilnost podjetja in njegovo sposobnost ustvarjanja prihodkov na trgu."""
    
    sistem_plan = """ Sistem za podporo pri večkriterijskem odločanju je zasnovan tako, da vključuje vse ključne
                    funkcionalne in nefunkcionalne zahteve. Funkcionalno aplikacija uporabnikom omogoča izbiro """
    
    method_implement = """  TOPSIS temelji na identifikaciji rešitev, ki so najbližje idealni rešitvi in najdlje od najslabše možne rešitve. 
                    Proces vključuje normalizacijo podatkov, izračun razdalj od pozitivnega in negativnega ideala ter določanje rangov. """
    
    result_comparison = """ Razvrščanje podjetij na podlagi različnih metod MCDA je ključno za razumevanje, kako se odločitve
                    lahko
                    spreminjajo glede na izbrane kriterije in metode. """
    
    user_decision = """  Na podlagi analiz, izvedenih z mojim sistemom za večkriterijsko odločanje (MCDA), bi investicijo v višini 
                    10.000 € razdelil med podjetja, ki so v večini metod MCDA dosegla najvišje ocene. Po uporabi metod, kot so  """
    
    testing = """ Za preverjanje pravilnega delovanja sistema smo uporabili več strategij testiranja. Na začetku smo
                    izvedli enotno testiranje, kjer smo posamično preverili vsako funkcijo sistema. """
    
    conclusion = """ Sistem za podporo odločanju, ki sem ga razvil, ponuja dragoceno orodje za analizo in razvrščanje podjetij
                    na podlagi kriterijev in uteži. Ključne ugotovitve in vpogledi poudarjajo učinkovitost metod MCDA pri """
    
    expected_results = """ Projekt se osredotoča na razvoj funkcionalne spletne aplikacije, ki vključuje metode MCDA, kot so
                    TOPSIS, PROMETHEE, VIKOR, WSM in MACBETH. Aplikacija omogoča uporabnikom intuitivno izkušnjo pri sprejemanju investicijskih odločitev z """
    
    return render_template('index.html', 
                           long_text=long_text, 
                           company_choice=company_choice, 
                           criteria_choice=criteria_choice, 
                           sistem_plan=sistem_plan,
                           method_implement=method_implement,
                           result_comparison=result_comparison,
                           user_decision=user_decision,
                           testing=testing,
                           conclusion=conclusion,
                           expected_results=expected_results
                           )
