from flask import render_template, redirect, url_for, abort, flash, session
from .forms import CompanySearchForm, CompanyAddForm, PortfolioAddForm
from .models import Company, db, Portfolio
import requests as req
from . import app
import requests
import json
from sqlalchemy.exc import DBAPIError, IntegrityError, InvalidRequestError
from .charts import make_5y_stock_chart, make_5y_vwap_chart

@app.add_template_global
def get_portfolios():
    return Portfolio.query.all()


@app.route('/')
def home():
    """Home route for stock portfolio"""
    return render_template('home.html')


@app.route('/search', methods=['GET', 'POST'])
def company_search():
    """
    """
    form = CompanySearchForm()

    # This path represents a POST
    if form.validate_on_submit():
        symbol = form.data['symbol']
        res = requests.get(f'https://api.iextrading.com/1.0/stock/{ symbol }/company')

        data = json.loads(res.text)
        session['context'] = data

        return redirect(url_for('.company_preview'))
    # This is a GET
    return render_template('portfolio/search.html', form=form)


@app.route('/preview', methods=['GET', 'POST'])
def company_preview():
    """
    """
    form_context = {
        'symbol': session['context']['symbol'],
        'companyName': session['context']['companyName'],
        'exchange': session['context']['exchange'],
        'industry': session['context']['industry'],
        'website': session['context']['website'],
        'description': session['context']['description'],
        'CEO': session['context']['CEO'],
        'issueType': session['context']['issueType'],
        'sector': session['context']['sector']
    }
    form = CompanyAddForm(**form_context)
    if form.validate_on_submit():
        try:
            company = Company(
                symbol=form.data['symbol'],
                portfolio_id=form.data['portfolios'],
                companyName=form.data['companyName'],
                exchange=form.data['exchange'],
                industry=form.data['industry'],
                website=form.data['website'],
                description=form.data['description'],
                CEO=form.data['CEO'],
                issueType=form.data['issueType'],
                sector=form.data['sector'],
            )
            db.session.add(company)
            db.session.commit()
        except (DBAPIError, IntegrityError, InvalidRequestError):
            flash('An error occurred trying to add the company.')
            # Error in writing to db. End this req/res cycle and render search page.
            return render_template('portfolio/search.html', form=form)
        # Write was successful. Redirect to portfolio detail page
        print('Company added to the database.')
        return redirect(url_for('.portfolio_detail'))
    # This was a POST method. Render the portfolio preview with form context
    return render_template('portfolio/preview.html', form=form, company_data=session['context'])


@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio_detail():
    """Give company detail
    """
    form = PortfolioAddForm()

    if form.validate_on_submit():
        try:
            portfolio = Portfolio(name=form.data['name'])
            db.session.add(portfolio)
            db.session.commit()
        except (DBAPIError, IntegrityError):
            flash('There was a problem creating the portfolio.')
            return render_template('portfolio/search.html', form=form)
        # Create portfolio was successful. Redirect to search.html
        return redirect(url_for('.company_search'))

    return render_template('portfolio/portfolio.html', form=form)
    companies = Company.query.all()
    return render_template('portfolio/portfolio.html', companies=companies)

