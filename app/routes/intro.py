from flask import Blueprint, render_template

intro_bp = Blueprint('intro', __name__)

##############################################################################
# UVODNA STRAN 
##############################################################################
@intro_bp.route('/intro')
def index():
    return render_template('intro.html')

@intro_bp.route('/companies_choice')
def companies_choice():
    return render_template('companies_choice.html')

@intro_bp.route('/criteria_choice')
def criteria_choice():
    return render_template('criteria_choice.html')

@intro_bp.route('/sistem_plan')
def sistem_plan():
    return render_template('sistem_plan.html')

@intro_bp.route('/method_implement')
def method_implement():
    return render_template('method_implement.html')

@intro_bp.route('/result_comparison')
def result_comparison():
    return render_template('result_comparison.html')

@intro_bp.route('/user_decision')
def user_decision():
    return render_template('user_decision.html')

@intro_bp.route('/testing')
def testing():
    return render_template('testing.html')

@intro_bp.route('/conclusion')
def conclusion():
    return render_template('conclusion.html')

@intro_bp.route('/expected_results')
def expected_results():
    return render_template('expected_results.html')